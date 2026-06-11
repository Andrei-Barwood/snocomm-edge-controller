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
from multiprocessing import shared_memory, Event

logger = logging.getLogger("SignalGenerator")

class RealTimeSignalGenerator:
    def __init__(self, config, data_ready_event):
        self.fs = config['network']['sampling_rate']
        self.batch_size = config['network']['samples_per_batch']
        self.nom_freq = config['network']['nominal_frequency']
        
        # We simulate 3 phases of Load Current
        self.num_channels = 3
        self.dtype = np.float64
        self.bytes_per_batch = self.batch_size * self.num_channels * np.dtype(self.dtype).itemsize
        
        # Shared memory and sync events
        self.shm = shared_memory.SharedMemory(create=True, size=self.bytes_per_batch)
        self.data_ready_event = data_ready_event
        
        # Link a numpy array to the shared memory buffer
        self.shared_array = np.ndarray((self.num_channels, self.batch_size), dtype=self.dtype, buffer=self.shm.buf)
        
        self.t = 0.0 # Global time
        self.dt = 1.0 / self.fs
        
        # Signal state
        self.current_freq = self.nom_freq
        self.phase_offset = 0.0
        
    def generate_batch(self):
        # Emulate frequency drift (random walk between 49.8 and 50.2)
        drift = np.random.normal(0, 0.001)
        self.current_freq += drift
        self.current_freq = np.clip(self.current_freq, 49.8, 50.2)
        
        # Generate time vector for the batch
        t_vec = self.t + np.arange(self.batch_size) * self.dt
        self.t += self.batch_size * self.dt
        
        # Angular frequency and phase
        omega = 2 * np.pi * self.current_freq
        theta = omega * t_vec + self.phase_offset
        
        # Fundamental (100A peak)
        i_a = 100.0 * np.sin(theta)
        i_b = 100.0 * np.sin(theta - 2*np.pi/3)
        i_c = 100.0 * np.sin(theta + 2*np.pi/3)
        
        # 3rd harmonic (20% -> 20A) - Zero sequence
        h3_a = 20.0 * np.sin(3 * theta)
        h3_b = 20.0 * np.sin(3 * (theta - 2*np.pi/3)) # 3*theta - 2pi = 3*theta
        h3_c = 20.0 * np.sin(3 * (theta + 2*np.pi/3)) # 3*theta + 2pi = 3*theta
        
        # 5th harmonic (10% -> 10A) - Negative sequence
        h5_a = 10.0 * np.sin(5 * theta)
        h5_b = 10.0 * np.sin(5 * (theta - 2*np.pi/3))
        h5_c = 10.0 * np.sin(5 * (theta + 2*np.pi/3))
        
        # 7th harmonic (5% -> 5A) - Positive sequence
        h7_a = 5.0 * np.sin(7 * theta)
        h7_b = 5.0 * np.sin(7 * (theta - 2*np.pi/3))
        h7_c = 5.0 * np.sin(7 * (theta + 2*np.pi/3))
        
        # Add some noise
        noise_a = np.random.normal(0, 0.5, self.batch_size)
        noise_b = np.random.normal(0, 0.5, self.batch_size)
        noise_c = np.random.normal(0, 0.5, self.batch_size)
        
        # Combine
        self.shared_array[0, :] = i_a + h3_a + h5_a + h7_a + noise_a
        self.shared_array[1, :] = i_b + h3_b + h5_b + h7_b + noise_b
        self.shared_array[2, :] = i_c + h3_c + h5_c + h7_c + noise_c

    def run(self, stop_event):
        logger.info(f"Signal Generator started. Shared Memory Name: {self.shm.name}")
        batch_duration = self.batch_size / self.fs
        
        try:
            while not stop_event.is_set():
                t_start = time.perf_counter()
                
                self.generate_batch()
                self.data_ready_event.set() # Notify HRT process
                
                # Sleep to emulate real-time ADC pacing
                t_end = time.perf_counter()
                elapsed = t_end - t_start
                sleep_time = batch_duration - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    self.data_ready_event.clear() # Reset if we overrun
        finally:
            self.shm.close()
            self.shm.unlink()
            logger.info("Signal Generator stopped and shared memory cleaned up.")

def start_generator_process(config, stop_event, shm_name_queue, data_ready_event):
    # This function is the entry point for the multiprocessing.Process
    generator = RealTimeSignalGenerator(config, data_ready_event)
    shm_name_queue.put(generator.shm.name)
    generator.run(stop_event)
