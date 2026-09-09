"""Convierte una campaña importada en telemetría del Monitor / DSP."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any

import numpy as np

from dsp.core import (
    CHANNEL_IA,
    CHANNEL_IB,
    CHANNEL_IC,
    CHANNEL_IN,
    CHANNEL_VA,
    CHANNEL_VB,
    CHANNEL_VC,
    NUM_CHANNELS,
    BlockDspController,
    rms,
)
from dsp.patterns import PatternSpec, generate_pattern_batch

from .parser import ParsedTable

DSP_FS = 12_800.0
BATCH = 128
V_LN_RMS = 230.0


@dataclass
class ImportResult:
    telemetry: dict[str, Any]
    meta: dict[str, Any]
    warnings: list[str] = field(default_factory=list)


def _series(table: ParsedTable, channel: str) -> np.ndarray | None:
    header = table.mapping.get(channel)
    if header is None:
        return None
    if header not in table.columns:
        return None
    values = np.asarray(table.columns[header], dtype=float)
    if values.size == 0 or np.all(np.isnan(values)):
        return None
    return np.nan_to_num(values, nan=0.0)


def _infer_fs(time: np.ndarray | None, declared: float | None) -> float:
    if declared and declared > 1.0:
        return float(declared)
    if time is None or time.size < 3:
        return DSP_FS
    delta = np.diff(time)
    delta = delta[np.isfinite(delta) & (delta > 0)]
    if delta.size == 0:
        return DSP_FS
    step = float(np.median(delta))
    if step > 1.0:
        step /= 1000.0
    if step <= 0:
        return DSP_FS
    return 1.0 / step


def _resample(values: np.ndarray, t_src: np.ndarray, t_dst: np.ndarray) -> np.ndarray:
    return np.interp(t_dst, t_src, values)


def _build_batch(
    table: ParsedTable,
    fs: float,
    current_scale: float,
    voltage_scale: float,
) -> tuple[np.ndarray, list[str], list[str]]:
    notes: list[str] = []
    used: list[str] = []
    time = _series(table, "time")
    ia = _series(table, "ia")
    ib = _series(table, "ib")
    ic = _series(table, "ic")
    i_n = _series(table, "in")
    va = _series(table, "va")
    vb = _series(table, "vb")
    vc = _series(table, "vc")

    if ia is None and ib is None and ic is None and i_n is None:
        raise ValueError("No hay canales de corriente mapeados (ia/ib/ic/in).")

    length = max(
        len(item)
        for item in (time, ia, ib, ic, i_n, va, vb, vc)
        if item is not None
    )
    if time is None:
        time = np.arange(length, dtype=float) / fs
        notes.append("Tiempo sintético a partir de la frecuencia de muestreo.")
    if time.size > 3 and float(np.median(np.diff(time))) > 0.05:
        time = time / 1000.0
        notes.append("La columna de tiempo se interpretó en milisegundos.")

    t0, t1 = float(time[0]), float(time[-1])
    if t1 <= t0:
        raise ValueError("El eje de tiempo no es creciente.")
    t_dst = np.arange(t0, t1, 1.0 / DSP_FS)
    if t_dst.size < BATCH:
        raise ValueError(
            f"La captura es demasiado corta ({t_dst.size} muestras a 12.8 kHz). "
            "Exporte al menos ~20 ms."
        )
    if t_dst.size > DSP_FS * 2.5:
        t_dst = t_dst[: int(DSP_FS * 2.5)]
        notes.append("Se usaron los primeros 2.5 s para no saturar el DSP.")

    def take(signal: np.ndarray | None, scale: float, name: str) -> np.ndarray:
        if signal is None:
            return np.zeros_like(t_dst)
        used.append(name)
        src_t = time[: len(signal)]
        return _resample(signal[: len(src_t)] * scale, src_t, t_dst)

    ia_s = take(ia, current_scale, "ia")
    ib_s = take(ib, current_scale, "ib")
    ic_s = take(ic, current_scale, "ic")
    if i_n is None:
        in_s = ia_s + ib_s + ic_s
        notes.append("In = Ia+Ib+Ic (no venía en el archivo).")
    else:
        in_s = take(i_n, current_scale, "in")

    if va is None and vb is None and vc is None:
        omega = 2.0 * math.pi * 50.0
        peak = V_LN_RMS * math.sqrt(2.0)
        va_s = peak * np.sin(omega * t_dst)
        vb_s = peak * np.sin(omega * t_dst - 2.0 * math.pi / 3.0)
        vc_s = peak * np.sin(omega * t_dst + 2.0 * math.pi / 3.0)
        notes.append("Tensión PCC sintetizada a 230 V / 50 Hz para el PLL.")
    else:
        va_s = take(va, voltage_scale, "va")
        vb_s = take(vb, voltage_scale, "vb")
        vc_s = take(vc, voltage_scale, "vc")

    batch = np.vstack([ia_s, ib_s, ic_s, in_s, va_s, vb_s, vc_s])
    assert batch.shape[0] == NUM_CHANNELS
    return batch, used, notes


def _run_dsp(batch: np.ndarray) -> dict[str, Any]:
    dsp = BlockDspController(
        sampling_rate=DSP_FS,
        nominal_frequency=50.0,
        kp=0.5,
        ki=5.0,
        max_current_rms=200.0,
        voltage_ln_rms=V_LN_RMS,
    )
    result = None
    windows = max(1, batch.shape[1] // BATCH)
    for index in range(windows):
        start = index * BATCH
        chunk = batch[:, start : start + BATCH]
        if chunk.shape[1] < BATCH:
            break
        result = dsp.process(chunk)
    if result is None:
        raise ValueError("No hubo ventanas DSP completas.")
    payload = result.to_dict()
    payload["source"] = "imported"
    return payload


def _telemetry_from_registers(registers: dict[str, float]) -> dict[str, Any]:
    i1 = registers.get("i1_rms")
    if i1 is None:
        i1 = registers.get("ia_rms", 0.0)
    h3 = registers.get("h3_rms", 0.0)
    h5 = registers.get("h5_rms", 0.0)
    h7 = registers.get("h7_rms", 0.0)
    thdi = registers.get("thdi")
    if thdi is None and i1:
        ih = math.sqrt(h3 * h3 + h5 * h5 + h7 * h7)
        thdi = 100.0 * ih / i1 if i1 else 0.0
    zeros = [0.0] * BATCH
    return {
        "frame_count": 1,
        "t_dsp_ms": 0.0,
        "freq_est": registers.get("freq_est", 50.0),
        "theta": 0.0,
        "thdi": float(thdi or 0.0),
        "thdi_method": "registros del instrumento (no Ih/I1 del DSP)",
        "i1_rms": float(i1 or 0.0),
        "h3_rms": float(h3),
        "h5_rms": float(h5),
        "h7_rms": float(h7),
        "in_rms": float(registers.get("in_rms", 0.0)),
        "i_comp_rms": math.sqrt(h3 * h3 + h5 * h5 + h7 * h7),
        "is_saturated": False,
        "pll_source": "instrument",
        "sequence_model": "registers",
        "raw_waveform": zeros,
        "comp_waveform": zeros,
        "raw_neutral": zeros,
        "voltage_waveform": zeros,
        "disclaimer": "Valores declarados por la central/medidor. No son formas de onda muestreadas.",
        "source": "imported",
        "vdc": registers.get("vdc"),
        "idc": registers.get("idc"),
    }


def process_campaign(
    table: ParsedTable | None,
    registers: dict[str, float] | None = None,
    *,
    fs: float | None = None,
    current_scale: float = 1.0,
    voltage_scale: float = 1.0,
    filename: str = "campaign",
) -> ImportResult:
    warnings = list(table.warnings) if table else []
    registers = registers or {}

    if table is None:
        if not registers:
            raise ValueError("El archivo no trae formas de onda ni registros numéricos.")
        telemetry = _telemetry_from_registers(registers)
        return ImportResult(
            telemetry=telemetry,
            meta={
                "filename": filename,
                "mode": "registers",
                "mapping": {},
                "headers": [],
                "samples": 0,
            },
            warnings=warnings + ["Solo registros: el gráfico de onda queda vacío."],
        )

    time = _series(table, "time")
    inferred = _infer_fs(time, fs)
    batch, used, notes = _build_batch(table, inferred, current_scale, voltage_scale)
    warnings.extend(notes)
    telemetry = _run_dsp(batch)
    if registers.get("thdi") is not None:
        warnings.append(
            f"La central declara THDi={registers['thdi']}% ; "
            f"el DSP de la captura calcula {telemetry['thdi']:.1f}%."
        )
    return ImportResult(
        telemetry=telemetry,
        meta={
            "filename": filename,
            "mode": "waveforms",
            "mapping": table.mapping,
            "headers": table.headers,
            "used_channels": used,
            "samples": int(batch.shape[1]),
            "fs_inferred_hz": inferred,
            "fs_dsp_hz": DSP_FS,
            "duration_s": batch.shape[1] / DSP_FS,
            "ia_rms": rms(batch[CHANNEL_IA]),
            "in_rms": rms(batch[CHANNEL_IN]),
        },
        warnings=warnings,
    )


def example_scope_csv() -> str:
    """CSV estilo osciloscopio para pruebas y para el usuario."""
    spec = PatternSpec(
        name="demo",
        description="captura de ejemplo",
        i1_peak=10.0,
        h3_peak=2.0,
        h5_peak=1.0,
        h7_peak=0.5,
        noise_rms=0.0,
        freq_drift=False,
    )
    batch, _, _ = generate_pattern_batch(spec, 0.0, 10_000.0, 4000)
    t = np.arange(batch.shape[1]) / 10_000.0
    lines = ["Time,CH1,CH2,CH3,CH4"]
    for i in range(batch.shape[1]):
        lines.append(
            f"{t[i]:.6f},{batch[CHANNEL_IA, i]:.5f},{batch[CHANNEL_IB, i]:.5f},"
            f"{batch[CHANNEL_IC, i]:.5f},{batch[CHANNEL_IN, i]:.5f}"
        )
    return "\n".join(lines)
