"""Núcleo DSP 3P+N independiente de memoria compartida y del lazo de procesos.

El PLL se sincroniza a la tensión del PCC. El 3.er armónico se extrae del eje
cero / neutro; el 5.º como secuencia negativa y el 7.º como secuencia positiva.
THDi = Ih / I1, no Ih / Irms_total.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import time
from typing import Any

import numpy as np

SQRT3_2 = math.sqrt(3.0) / 2.0
TWO_THIRDS = 2.0 / 3.0

CHANNEL_IA = 0
CHANNEL_IB = 1
CHANNEL_IC = 2
CHANNEL_IN = 3
CHANNEL_VA = 4
CHANNEL_VB = 5
CHANNEL_VC = 6
NUM_CHANNELS = 7


def clarke_ab0(
    ia: np.ndarray, ib: np.ndarray, ic: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Transformada de Clarke amplitud-invariante con componente de secuencia cero."""
    alpha = TWO_THIRDS * (ia - 0.5 * ib - 0.5 * ic)
    beta = TWO_THIRDS * (SQRT3_2 * ib - SQRT3_2 * ic)
    zero = (ia + ib + ic) / 3.0
    return alpha, beta, zero


def inverse_clarke(
    alpha: np.ndarray, beta: np.ndarray, zero: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Inversa de Clarke amplitud-invariante."""
    ia = alpha + zero
    ib = -0.5 * alpha + SQRT3_2 * beta + zero
    ic = -0.5 * alpha - SQRT3_2 * beta + zero
    return ia, ib, ic


def rms(signal: np.ndarray) -> float:
    """RMS de una secuencia 1-D."""
    if signal.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(signal))))


def thdi_percent(i1_rms: float, harmonic_rms: list[float]) -> float:
    """THDi académico de las componentes declaradas: 100 · Ih / I1."""
    if i1_rms <= 1e-9:
        return 0.0
    ih = math.sqrt(sum(value * value for value in harmonic_rms))
    return 100.0 * ih / i1_rms


def _wrap_angle(theta: float) -> float:
    two_pi = 2.0 * math.pi
    theta = math.fmod(theta, two_pi)
    if theta < 0.0:
        theta += two_pi
    return theta


def _lpf_step(state: float, sample: float, alpha: float) -> float:
    return state + alpha * (sample - state)


@dataclass
class DSPResult:
    """Salida de un microbloque DSP, lista para telemetría y el proyecto común."""

    frame_count: int
    t_dsp_ms: float
    freq_est: float
    theta: float
    thdi: float
    thdi_method: str
    i1_rms: float
    h3_rms: float
    h5_rms: float
    h7_rms: float
    in_rms: float
    i_comp_rms: float
    is_saturated: bool
    pll_source: str
    sequence_model: str
    raw_waveform: list[float]
    comp_waveform: list[float]
    raw_neutral: list[float]
    voltage_waveform: list[float]
    disclaimer: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class _DqState:
    d: float = 0.0
    q: float = 0.0


class BlockDspController:
    """Procesador por microbloques. No garantiza hard real-time."""

    THDI_METHOD = "Ih(3+5+7) / I1 · 100"
    PLL_SOURCE = "voltage_pcc"
    SEQUENCE_MODEL = "ab0_3p4w"
    DISCLAIMER = (
        "Indicador académico de desarrollo. No es THD según IEC 61000-4-7/-4-30 "
        "ni evidencia de cumplimiento SEC."
    )

    def __init__(
        self,
        sampling_rate: float,
        nominal_frequency: float,
        kp: float,
        ki: float,
        max_current_rms: float,
        voltage_ln_rms: float = 230.0,
        delay_samples: int = 2,
        lpf_cutoff_hz: float = 5.0,
    ) -> None:
        self.fs = float(sampling_rate)
        self.dt = 1.0 / self.fs
        self.nom_freq = float(nominal_frequency)
        self.kp = float(kp)
        self.ki = float(ki)
        self.max_current = float(max_current_rms)
        self.v_base = float(voltage_ln_rms) * math.sqrt(2.0)
        self.delay_samples = int(delay_samples)
        tau = 1.0 / (2.0 * math.pi * lpf_cutoff_hz)
        self.lpf_alpha = self.dt / (tau + self.dt)
        self.theta = 0.0
        self.omega = 2.0 * math.pi * self.nom_freq
        self.pll_integrator = 0.0
        self.frame_count = 0
        self._dq: dict[str, _DqState] = {
            "i1": _DqState(),
            "h3": _DqState(),
            "h5": _DqState(),
            "h7": _DqState(),
        }

    def reset(self) -> None:
        self.theta = 0.0
        self.omega = 2.0 * math.pi * self.nom_freq
        self.pll_integrator = 0.0
        self.frame_count = 0
        for state in self._dq.values():
            state.d = 0.0
            state.q = 0.0

    def srf_pll(self, v_alpha: np.ndarray, v_beta: np.ndarray) -> tuple[np.ndarray, float]:
        """SRF-PLL sobre tensión del PCC, normalizada a la tensión de base."""
        n = len(v_alpha)
        theta_array = np.empty(n, dtype=float)
        freq_est = self.nom_freq
        v_base = max(self.v_base, 1.0)
        for i in range(n):
            va = v_alpha[i] / v_base
            vb = v_beta[i] / v_base
            # Convención seno: α=V sin(ωt), β=-V cos(ωt). El error de fase es vd, no vq.
            v_d = va * math.cos(self.theta) + vb * math.sin(self.theta)
            self.pll_integrator += self.ki * v_d * self.dt
            delta_omega = self.kp * v_d + self.pll_integrator
            self.omega = 2.0 * math.pi * self.nom_freq + delta_omega
            self.theta = _wrap_angle(self.theta + self.omega * self.dt)
            theta_array[i] = self.theta
            freq_est = self.omega / (2.0 * math.pi)
        return theta_array, freq_est

    def _extract_ab(
        self,
        key: str,
        alpha: np.ndarray,
        beta: np.ndarray,
        theta: np.ndarray,
        harmonic: int,
        sequence: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Park + LPF + Park inversa. sequence=+1 positiva, -1 negativa."""
        theta_n = sequence * harmonic * theta
        cos_th = np.cos(theta_n)
        sin_th = np.sin(theta_n)
        i_d = alpha * cos_th + beta * sin_th
        i_q = -alpha * sin_th + beta * cos_th
        d_dc = np.empty_like(i_d)
        q_dc = np.empty_like(i_q)
        state = self._dq[key]
        d_val, q_val = state.d, state.q
        alpha_lpf = self.lpf_alpha
        for i in range(len(i_d)):
            d_val = _lpf_step(d_val, float(i_d[i]), alpha_lpf)
            q_val = _lpf_step(q_val, float(i_q[i]), alpha_lpf)
            d_dc[i] = d_val
            q_dc[i] = q_val
        state.d, state.q = d_val, q_val
        h_alpha = d_dc * cos_th - q_dc * sin_th
        h_beta = d_dc * sin_th + q_dc * cos_th
        return h_alpha, h_beta

    def _extract_zero(self, i0: np.ndarray, theta: np.ndarray, harmonic: int) -> np.ndarray:
        """Demodulación síncrona del eje cero (3.er armónico de secuencia cero)."""
        n_theta = harmonic * theta
        cos_th = np.cos(n_theta)
        sin_th = np.sin(n_theta)
        d_in = 2.0 * i0 * cos_th
        q_in = 2.0 * i0 * sin_th
        d_dc = np.empty_like(i0)
        q_dc = np.empty_like(i0)
        state = self._dq["h3"]
        d_val, q_val = state.d, state.q
        alpha_lpf = self.lpf_alpha
        for i in range(len(i0)):
            d_val = _lpf_step(d_val, float(d_in[i]), alpha_lpf)
            q_val = _lpf_step(q_val, float(q_in[i]), alpha_lpf)
            d_dc[i] = d_val
            q_dc[i] = q_val
        state.d, state.q = d_val, q_val
        return d_dc * cos_th + q_dc * sin_th

    def _apply_priority_limit(
        self, components: dict[int, np.ndarray]
    ) -> tuple[np.ndarray, bool]:
        """Si la referencia supera el límite, reduce primero 7, luego 5, luego 3."""
        order = [7, 5, 3]
        total = sum(components.values())
        saturated = rms(total[0]) > self.max_current
        if not saturated:
            return total, False
        for harmonic in order:
            rest = sum(wave for key, wave in components.items() if key != harmonic)
            rest_rms = rms(rest[0])
            if rest_rms >= self.max_current:
                components[harmonic][:] = 0.0
                continue
            budget = math.sqrt(max(self.max_current**2 - rest_rms**2, 0.0))
            current = rms(components[harmonic][0])
            if current > budget and current > 1e-9:
                components[harmonic] *= budget / current
            break
        return sum(components.values()), True

    def process(self, batch: np.ndarray) -> DSPResult:
        """Procesa un lote (7, N): Ia Ib Ic In Va Vb Vc."""
        if batch.ndim != 2 or batch.shape[0] < NUM_CHANNELS:
            raise ValueError(f"Se espera un lote de forma ({NUM_CHANNELS}, N).")
        t0 = time.perf_counter()
        ia, ib, ic = batch[CHANNEL_IA], batch[CHANNEL_IB], batch[CHANNEL_IC]
        measured_in = batch[CHANNEL_IN]
        va, vb, vc = batch[CHANNEL_VA], batch[CHANNEL_VB], batch[CHANNEL_VC]

        i_alpha, i_beta, i0 = clarke_ab0(ia, ib, ic)
        v_alpha, v_beta, _v0 = clarke_ab0(va, vb, vc)
        theta, freq_est = self.srf_pll(v_alpha, v_beta)

        fund_a, fund_b = self._extract_ab("i1", i_alpha, i_beta, theta, 1, +1)
        zeros = np.zeros_like(i0)
        i1_a, _i1_b, _i1_c = inverse_clarke(fund_a, fund_b, zeros)

        h3_0 = self._extract_zero(i0, theta, 3)
        h5_a, h5_b = self._extract_ab("h5", i_alpha, i_beta, theta, 5, -1)
        h7_a, h7_b = self._extract_ab("h7", i_alpha, i_beta, theta, 7, +1)

        h5_ia, h5_ib, h5_ic = inverse_clarke(h5_a, h5_b, zeros)
        h7_ia, h7_ib, h7_ic = inverse_clarke(h7_a, h7_b, zeros)
        h3_ia, h3_ib, h3_ic = h3_0, h3_0, h3_0

        components = {
            3: -np.vstack([h3_ia, h3_ib, h3_ic]),
            5: -np.vstack([h5_ia, h5_ib, h5_ic]),
            7: -np.vstack([h7_ia, h7_ib, h7_ic]),
        }
        comp_abc, is_saturated = self._apply_priority_limit(components)
        in_comp = comp_abc[0] + comp_abc[1] + comp_abc[2]

        i1_rms = rms(i1_a)
        h3_rms = rms(h3_ia)
        h5_rms = rms(h5_ia)
        h7_rms = rms(h7_ia)
        thdi = thdi_percent(i1_rms, [h3_rms, h5_rms, h7_rms])

        self.frame_count += 1
        t_dsp_ms = (time.perf_counter() - t0) * 1000.0
        return DSPResult(
            frame_count=self.frame_count,
            t_dsp_ms=t_dsp_ms,
            freq_est=freq_est,
            theta=float(theta[-1]),
            thdi=thdi,
            thdi_method=self.THDI_METHOD,
            i1_rms=i1_rms,
            h3_rms=h3_rms,
            h5_rms=h5_rms,
            h7_rms=h7_rms,
            in_rms=rms(measured_in),
            i_comp_rms=rms(comp_abc[0]),
            is_saturated=is_saturated,
            pll_source=self.PLL_SOURCE,
            sequence_model=self.SEQUENCE_MODEL,
            raw_waveform=ia.astype(float).tolist(),
            comp_waveform=comp_abc[0].astype(float).tolist(),
            raw_neutral=measured_in.astype(float).tolist(),
            voltage_waveform=va.astype(float).tolist(),
            disclaimer=self.DISCLAIMER,
        )
