"""
Project: AHF Edge Controller
Type: Open Source
License: MIT
Owner: snocomm (prohibido venderlo)
Author: ਕਿਰਤਅਨ ਤੈਗ ਸਿਨਗਹ (Kirtan Teg Singh)
"""
import numpy as np
import time
import logging
from multiprocessing import shared_memory
import math

logger = logging.getLogger("HRT_Loop")

# Constantes Clarke
SQRT3_2 = math.sqrt(3) / 2
TWO_THIRDS = 2 / 3

class HardRealTimeController:
    def __init__(self, config, shm_name, data_ready_event, telemetry_queue):
        self.config = config
        self.fs = config['network']['sampling_rate']
        self.dt = 1.0 / self.fs
        self.batch_size = config['network']['samples_per_batch']
        self.nom_freq = config['network']['nominal_frequency']
        self.max_current = config['hardware']['max_current_rms']
        
        # PLL params
        self.kp = config['pll']['kp']
        self.ki = config['pll']['ki']
        self.theta = 0.0
        self.omega = 2 * np.pi * self.nom_freq
        self.pll_integrator = 0.0
        
        # LPF states for harmonics (simple exponential moving average for speed)
        # alpha = dt / (tau + dt), for a cutoff of ~5Hz, tau = 1/(2*pi*5) = 0.0318
        self.lpf_alpha = self.dt / (0.0318 + self.dt)
        self.harm_state = {3: {'d': 0.0, 'q': 0.0}, 5: {'d': 0.0, 'q': 0.0}, 7: {'d': 0.0, 'q': 0.0}}
        
        self.data_ready_event = data_ready_event
        self.telemetry_queue = telemetry_queue
        
        # Shared memory setup
        self.num_channels = 3
        self.dtype = np.float64
        self.bytes_per_batch = self.batch_size * self.num_channels * np.dtype(self.dtype).itemsize
        self.shm = shared_memory.SharedMemory(name=shm_name)
        self.shared_array = np.ndarray((self.num_channels, self.batch_size), dtype=self.dtype, buffer=self.shm.buf)
        
        # Delay compensation
        self.delay_samples = config['dsp']['system_delay_samples']

    def srf_pll(self, v_alpha, v_beta):
        """Sample-by-sample SRF-PLL"""
        theta_array = np.zeros(self.batch_size)
        freq_est = self.nom_freq
        
        for i in range(self.batch_size):
            # Park transform (only q-axis needed for PLL)
            v_q = -v_alpha[i] * math.sin(self.theta) + v_beta[i] * math.cos(self.theta)
            
            # PI Controller
            error = v_q
            self.pll_integrator += self.ki * error * self.dt
            delta_omega = self.kp * error + self.pll_integrator
            
            self.omega = 2 * math.pi * self.nom_freq + delta_omega
            self.theta += self.omega * self.dt
            
            # Wrap theta to 0-2PI
            if self.theta >= 2 * math.pi:
                self.theta -= 2 * math.pi
            elif self.theta < 0:
                self.theta += 2 * math.pi
                
            theta_array[i] = self.theta
            freq_est = self.omega / (2 * math.pi)
            
        return theta_array, freq_est

    def extract_harmonic(self, n, i_alpha, i_beta, theta_array):
        """Vectorized Multi-SRF extraction for harmonic n"""
        # If n is negative sequence (like 5th), rotation is opposite. 
        # But we can just use generic mathematical rotation.
        # 3rd is zero-sequence in balanced systems, but we process it anyway.
        # Actually in 3-phase 3-wire, 3rd doesn't exist. In 4-wire it does.
        # Assuming 4-wire or unbalanced for generality.
        
        theta_n = n * theta_array
        cos_th = np.cos(theta_n)
        sin_th = np.sin(theta_n)
        
        # Park
        i_d = i_alpha * cos_th + i_beta * sin_th
        i_q = -i_alpha * sin_th + i_beta * cos_th
        
        # Low pass filter (recursive EMA) to extract DC component
        # We can approximate by taking the mean of the batch if batch is small, 
        # but a true IIR is better.
        d_dc = np.zeros_like(i_d)
        q_dc = np.zeros_like(i_q)
        
        d_val = self.harm_state[n]['d']
        q_val = self.harm_state[n]['q']
        
        for i in range(self.batch_size):
            d_val += self.lpf_alpha * (i_d[i] - d_val)
            q_val += self.lpf_alpha * (i_q[i] - q_val)
            d_dc[i] = d_val
            q_dc[i] = q_val
            
        self.harm_state[n]['d'] = d_val
        self.harm_state[n]['q'] = q_val
        
        # Inverse Park to get harmonic in alpha-beta
        h_alpha = d_dc * cos_th - q_dc * sin_th
        h_beta = d_dc * sin_th + q_dc * cos_th
        
        return h_alpha, h_beta

    def run(self, stop_event):
        logger.info("HRT Loop started.")
        frame_count = 0
        
        try:
            while not stop_event.is_set():
                # Wait for data
                if not self.data_ready_event.wait(timeout=1.0):
                    continue
                self.data_ready_event.clear()
                
                t0 = time.perf_counter()
                
                # Copy from shared memory
                i_abc = self.shared_array.copy()
                
                # 1. Clarke Transform (abc to alpha-beta)
                i_alpha = TWO_THIRDS * (i_abc[0] - 0.5 * i_abc[1] - 0.5 * i_abc[2])
                i_beta = TWO_THIRDS * (SQRT3_2 * i_abc[1] - SQRT3_2 * i_abc[2])
                
                # 2. SRF-PLL
                # We use phase A as proxy for PLL reference if we were doing voltage, 
                # but here we use i_alpha, i_beta directly assuming current follows voltage phase.
                # In a real AHF, PLL locks to Voltage, but we only simulated current.
                theta_array, freq_est = self.srf_pll(i_alpha, i_beta)
                
                # Predictive phase shift for the DAC output (delay compensation)
                # We want to inject exactly in phase when the signal hits the grid.
                theta_pred = theta_array + (self.omega * self.dt * self.delay_samples)
                
                # 3. Harmonic Extraction & Saturation Logic
                comp_abc = np.zeros_like(i_abc)
                harm_rms_vals = {}
                
                # We want to inject INVERSE harmonics (contrafase), so we subtract them.
                for n in [3, 5, 7]:
                    h_alpha, h_beta = self.extract_harmonic(n, i_alpha, i_beta, theta_array)
                    
                    # Inverse Clarke
                    h_a = h_alpha
                    h_b = -0.5 * h_alpha + SQRT3_2 * h_beta
                    h_c = -0.5 * h_alpha - SQRT3_2 * h_beta
                    
                    # Contrafase
                    comp_n_abc = np.vstack([h_a, h_b, h_c]) * -1.0
                    
                    harm_rms_vals[n] = np.sqrt(np.mean(comp_n_abc[0]**2))
                    
                    # Accumulate (naive)
                    comp_abc += comp_n_abc
                
                # 4. Saturation and Prioritization (Simple RMS scaling)
                total_rms = np.sqrt(np.mean(comp_abc[0]**2))
                is_saturated = False
                
                if total_rms > self.max_current:
                    is_saturated = True
                    # If over limit, scale down (In a real system, we'd scale 7, then 5, etc.)
                    # For simplicity in this micro-batch, we apply a global scaling factor.
                    scale_factor = self.max_current / total_rms
                    comp_abc *= scale_factor
                
                t_dsp = time.perf_counter() - t0
                
                # Push telemetry every ~20 frames (~200ms) to not overwhelm TS
                frame_count += 1
                if frame_count % 20 == 0:
                    try:
                        # Compute Total THDi (approx)
                        rms_fund = np.sqrt(np.mean(i_abc[0]**2))
                        rms_harms = np.sqrt(harm_rms_vals[3]**2 + harm_rms_vals[5]**2 + harm_rms_vals[7]**2)
                        thdi = (rms_harms / rms_fund * 100) if rms_fund > 0 else 0
                        
                        payload = {
                            "frame_count": frame_count,
                            "t_dsp_ms": t_dsp * 1000,
                            "freq_est": freq_est,
                            "theta": theta_array[-1],
                            "thdi": thdi,
                            "h3_rms": harm_rms_vals[3],
                            "h5_rms": harm_rms_vals[5],
                            "h7_rms": harm_rms_vals[7],
                            "is_saturated": is_saturated,
                            "raw_waveform": i_abc[0].tolist(),     # Only phase A for UI
                            "comp_waveform": comp_abc[0].tolist()  # Only phase A for UI
                        }
                        if self.telemetry_queue.full():
                            self.telemetry_queue.get_nowait()
                        self.telemetry_queue.put_nowait(payload)
                    except Exception as e:
                        logger.warning(f"Telemetry queue error: {e}")

        finally:
            self.shm.close()
            logger.info("HRT Loop stopped.")

def start_hrt_process(config, stop_event, shm_name_queue, data_ready_event, telemetry_queue):
    shm_name = shm_name_queue.get() # Block until generator sends name
    controller = HardRealTimeController(config, shm_name, data_ready_event, telemetry_queue)
    controller.run(stop_event)
