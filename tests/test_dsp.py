"""Pruebas DSP contra señales patrón con error declarado."""

from __future__ import annotations

import math

import numpy as np
import pytest

from dsp.core import (
    BlockDspController,
    clarke_ab0,
    inverse_clarke,
    rms,
    thdi_percent,
)
from dsp.patterns import PatternSpec, generate_pattern_batch, pattern_catalog

FS = 12_800
BATCH = 128
SETTLE_SECONDS = 0.60
REL_TOL = 0.12


def _controller() -> BlockDspController:
    return BlockDspController(
        sampling_rate=FS,
        nominal_frequency=50.0,
        kp=0.5,
        ki=5.0,
        max_current_rms=200.0,
        voltage_ln_rms=230.0,
    )


def _run(spec: PatternSpec, seconds: float = SETTLE_SECONDS) -> tuple[BlockDspController, object]:
    dsp = _controller()
    t0 = 0.0
    freq = spec.frequency_hz
    result = None
    steps = int(seconds * FS / BATCH)
    for _ in range(steps):
        batch, freq, t0 = generate_pattern_batch(spec, t0, FS, BATCH, current_freq=freq)
        result = dsp.process(batch)
    assert result is not None
    return dsp, result


def _peak_to_rms(peak: float) -> float:
    return peak / math.sqrt(2.0)


def test_clarke_ab0_roundtrip():
    t = np.linspace(0, 1.0 / 50.0, 256, endpoint=False)
    ia = np.sin(2 * np.pi * 50 * t)
    ib = np.sin(2 * np.pi * 50 * t - 2 * np.pi / 3)
    ic = np.sin(2 * np.pi * 50 * t + 2 * np.pi / 3)
    alpha, beta, zero = clarke_ab0(ia, ib, ic)
    ra, rb, rc = inverse_clarke(alpha, beta, zero)
    assert np.allclose(ra, ia, atol=1e-9)
    assert np.allclose(rb, ib, atol=1e-9)
    assert np.allclose(rc, ic, atol=1e-9)
    assert np.max(np.abs(zero)) < 1e-9


def test_zero_sequence_appears_on_neutral_and_axis_0():
    spec = pattern_catalog()["zero_sequence_neutral"]
    batch, _, _ = generate_pattern_batch(spec, 0.0, FS, 256)
    ia, ib, ic, i_n = batch[0], batch[1], batch[2], batch[3]
    _alpha, _beta, i0 = clarke_ab0(ia, ib, ic)
    assert np.allclose(i_n, ia + ib + ic)
    assert rms(i_n) > 3.0 * _peak_to_rms(spec.h3_peak) * 0.9
    assert rms(i0) == pytest.approx(rms(i_n) / 3.0, rel=0.02)


def test_neutral_is_three_times_zero_sequence():
    spec = pattern_catalog()["zero_sequence_neutral"]
    batch, _, _ = generate_pattern_batch(spec, 0.0, FS, 256)
    _alpha, _beta, i0 = clarke_ab0(batch[0], batch[1], batch[2])
    assert abs(rms(batch[3]) - 3.0 * rms(i0)) < 0.05


def test_h3_extracted_from_zero_sequence():
    spec = pattern_catalog()["zero_sequence_neutral"]
    _dsp, result = _run(spec)
    expected = _peak_to_rms(spec.h3_peak)
    assert abs(result.h3_rms - expected) / expected <= REL_TOL
    assert result.h5_rms < 1.5
    assert result.h7_rms < 1.5


def test_h5_negative_sequence_extracted():
    spec = pattern_catalog()["negative_sequence_h5"]
    _dsp, result = _run(spec)
    expected = _peak_to_rms(spec.h5_peak)
    assert abs(result.h5_rms - expected) / expected <= REL_TOL
    assert result.h3_rms < 1.5
    assert result.h7_rms < 1.5


def test_h7_positive_sequence_extracted():
    spec = pattern_catalog()["positive_sequence_h7"]
    _dsp, result = _run(spec)
    expected = _peak_to_rms(spec.h7_peak)
    assert abs(result.h7_rms - expected) / expected <= REL_TOL
    assert result.h3_rms < 1.2
    assert result.h5_rms < 1.2


def test_thdi_uses_fundamental_not_total_rms():
    spec = PatternSpec(
        name="thdi",
        description="THDi conocido",
        i1_peak=100.0,
        h3_peak=20.0,
        h5_peak=10.0,
        h7_peak=5.0,
    )
    _dsp, result = _run(spec)
    expected_i1 = _peak_to_rms(100.0)
    expected_thdi = thdi_percent(
        expected_i1,
        [_peak_to_rms(20.0), _peak_to_rms(10.0), _peak_to_rms(5.0)],
    )
    assert abs(result.i1_rms - expected_i1) / expected_i1 <= REL_TOL
    assert abs(result.thdi - expected_thdi) <= 3.0
    from_components = thdi_percent(result.i1_rms, [result.h3_rms, result.h5_rms, result.h7_rms])
    assert result.thdi == pytest.approx(from_components, abs=1e-9)


def test_pll_locks_to_voltage_not_current():
    spec = pattern_catalog()["pll_voltage_vs_current"]
    _dsp, result = _run(spec, seconds=0.8)
    assert abs(result.freq_est - 50.0) < 0.15
    assert result.pll_source == "voltage_pcc"


def test_saturation_drops_h7_first():
    spec = PatternSpec(
        name="sat",
        description="fuerza saturación",
        i1_peak=100.0,
        h3_peak=20.0,
        h5_peak=20.0,
        h7_peak=20.0,
    )
    dsp = BlockDspController(
        sampling_rate=FS,
        nominal_frequency=50.0,
        kp=0.5,
        ki=5.0,
        max_current_rms=8.0,
        voltage_ln_rms=230.0,
    )
    t0 = 0.0
    result = None
    for _ in range(int(0.5 * FS / BATCH)):
        batch, _, t0 = generate_pattern_batch(spec, t0, FS, BATCH)
        result = dsp.process(batch)
    assert result is not None
    assert result.is_saturated is True
    assert result.i_comp_rms <= 8.0 + 0.6
