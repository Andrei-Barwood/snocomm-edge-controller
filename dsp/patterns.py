"""Señales patrón 3P+N con amplitud, fase, secuencia y frecuencia conocidas."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np

from .core import NUM_CHANNELS

TWO_PI = 2.0 * math.pi
SHIFT = 2.0 * math.pi / 3.0


@dataclass(frozen=True)
class PatternSpec:
    """Definición reproducible de un caso de señal."""

    name: str
    description: str
    frequency_hz: float = 50.0
    v_ln_rms: float = 230.0
    i1_peak: float = 100.0
    h3_peak: float = 0.0
    h5_peak: float = 0.0
    h7_peak: float = 0.0
    current_phase_lag_rad: float = 0.0
    noise_rms: float = 0.0
    freq_drift: bool = False


def pattern_catalog() -> dict[str, PatternSpec]:
    """Casos usados por el generador y por los tests DSP."""
    return {
        "fundamental_only": PatternSpec(
            name="fundamental_only",
            description="Tensión y corriente fundamentales equilibradas, sin armónicos.",
            i1_peak=100.0,
        ),
        "zero_sequence_neutral": PatternSpec(
            name="zero_sequence_neutral",
            description="3.er armónico de secuencia cero (se suma en el neutro 3P+N).",
            i1_peak=100.0,
            h3_peak=20.0,
        ),
        "negative_sequence_h5": PatternSpec(
            name="negative_sequence_h5",
            description="5.º armónico de secuencia negativa, típico de rectificador de 6 pulsos.",
            i1_peak=100.0,
            h5_peak=10.0,
        ),
        "positive_sequence_h7": PatternSpec(
            name="positive_sequence_h7",
            description="7.º armónico de secuencia positiva.",
            i1_peak=100.0,
            h7_peak=5.0,
        ),
        "combined_it": PatternSpec(
            name="combined_it",
            description="Carga TI académica: fundamental + H3 cero + H5 neg. + H7 pos.",
            i1_peak=100.0,
            h3_peak=20.0,
            h5_peak=10.0,
            h7_peak=5.0,
            noise_rms=0.5,
            freq_drift=True,
        ),
        "pll_voltage_vs_current": PatternSpec(
            name="pll_voltage_vs_current",
            description="Corriente atrasada 90°; el PLL debe seguir la tensión, no la corriente.",
            i1_peak=100.0,
            current_phase_lag_rad=math.pi / 2.0,
        ),
    }


def generate_pattern_batch(
    spec: PatternSpec,
    t0: float,
    sampling_rate: float,
    samples: int,
    current_freq: float | None = None,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, float, float]:
    """Genera un lote (7, N): Ia Ib Ic In Va Vb Vc.

    Returns:
        batch, frecuencia usada, tiempo final.
    """
    freq = spec.frequency_hz if current_freq is None else current_freq
    if spec.freq_drift:
        rng = rng or np.random.default_rng()
        freq = float(np.clip(freq + rng.normal(0.0, 0.001), 49.8, 50.2))

    dt = 1.0 / sampling_rate
    t_vec = t0 + np.arange(samples, dtype=float) * dt
    theta_v = TWO_PI * freq * t_vec
    theta_i = theta_v - spec.current_phase_lag_rad
    v_peak = spec.v_ln_rms * math.sqrt(2.0)

    va = v_peak * np.sin(theta_v)
    vb = v_peak * np.sin(theta_v - SHIFT)
    vc = v_peak * np.sin(theta_v + SHIFT)

    ia = spec.i1_peak * np.sin(theta_i)
    ib = spec.i1_peak * np.sin(theta_i - SHIFT)
    ic = spec.i1_peak * np.sin(theta_i + SHIFT)

    if spec.h3_peak:
        h3 = spec.h3_peak * np.sin(3.0 * theta_i)
        ia = ia + h3
        ib = ib + h3
        ic = ic + h3

    if spec.h5_peak:
        ia = ia + spec.h5_peak * np.sin(5.0 * theta_i)
        ib = ib + spec.h5_peak * np.sin(5.0 * theta_i + SHIFT)
        ic = ic + spec.h5_peak * np.sin(5.0 * theta_i - SHIFT)

    if spec.h7_peak:
        ia = ia + spec.h7_peak * np.sin(7.0 * theta_i)
        ib = ib + spec.h7_peak * np.sin(7.0 * (theta_i - SHIFT))
        ic = ic + spec.h7_peak * np.sin(7.0 * (theta_i + SHIFT))

    if spec.noise_rms > 0.0:
        rng = rng or np.random.default_rng()
        ia = ia + rng.normal(0.0, spec.noise_rms, samples)
        ib = ib + rng.normal(0.0, spec.noise_rms, samples)
        ic = ic + rng.normal(0.0, spec.noise_rms, samples)

    i_n = ia + ib + ic
    batch = np.vstack([ia, ib, ic, i_n, va, vb, vc])
    assert batch.shape == (NUM_CHANNELS, samples)
    return batch, freq, float(t0 + samples * dt)


def spec_to_dict(spec: PatternSpec) -> dict[str, Any]:
    return {
        "name": spec.name,
        "description": spec.description,
        "frequency_hz": spec.frequency_hz,
        "v_ln_rms": spec.v_ln_rms,
        "i1_peak": spec.i1_peak,
        "h3_peak": spec.h3_peak,
        "h5_peak": spec.h5_peak,
        "h7_peak": spec.h7_peak,
        "current_phase_lag_rad": spec.current_phase_lag_rad,
        "noise_rms": spec.noise_rms,
        "freq_drift": spec.freq_drift,
    }
