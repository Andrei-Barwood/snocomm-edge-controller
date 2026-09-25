"""Estadísticas de un CSV de osciloscopio, sin exigir canales de corriente."""

from __future__ import annotations

from typing import Any

import numpy as np

from acquisition.parser import parse_csv


def _finite(values: np.ndarray) -> np.ndarray:
    return values[np.isfinite(values)]


def _channel_stats(name: str, values: np.ndarray) -> dict[str, Any] | None:
    arr = _finite(np.asarray(values, dtype=float))
    if arr.size == 0:
        return None
    mean = float(np.mean(arr))
    rms = float(np.sqrt(np.mean(np.square(arr))))
    peak_min = float(np.min(arr))
    peak_max = float(np.max(arr))
    ripple = abs(peak_max - peak_min)
    ripple_pct = (ripple / abs(mean) * 100.0) if abs(mean) > 1e-9 else None
    return {
        "name": name,
        "samples": int(arr.size),
        "mean": round(mean, 4),
        "rms": round(rms, 4),
        "min": round(peak_min, 4),
        "max": round(peak_max, 4),
        "pp": round(ripple, 4),
        "std": round(float(np.std(arr)), 4),
        "ripple_pct": None if ripple_pct is None else round(ripple_pct, 3),
        "waveform": [round(float(v), 4) for v in arr[:: max(1, arr.size // 160)][:160]],
    }


def _infer_fs(time_col: np.ndarray | None) -> float | None:
    if time_col is None:
        return None
    t = _finite(time_col)
    if t.size < 3:
        return None
    dt = np.diff(t)
    dt = dt[np.isfinite(dt) & (dt > 0)]
    if dt.size == 0:
        return None
    return float(1.0 / np.median(dt))


def summarize_csv(text: str, filename: str = "") -> dict[str, Any]:
    """Parsea un CSV de scope y resume cada canal numérico."""
    table = parse_csv(text)
    channels: dict[str, dict[str, Any]] = {}
    for name, col in table.columns.items():
        stats = _channel_stats(name, col)
        if stats:
            channels[name] = stats

    mapping = dict(table.mapping)
    time_header = mapping.get("time")
    time_col = table.columns.get(time_header) if time_header else None
    fs = _infer_fs(time_col)

    def _mapped(key: str) -> dict[str, Any] | None:
        header = mapping.get(key)
        return channels.get(header) if header else None

    voltage = _mapped("va") or _mapped("vb") or _mapped("vc")
    current = _mapped("ia") or _mapped("ib") or _mapped("ic")
    if voltage is None:
        for stats in channels.values():
            if stats["name"] == time_header:
                continue
            if 15.0 <= abs(stats["mean"]) <= 32.0:
                voltage = stats
                break
    if voltage is None:
        for name, stats in channels.items():
            if name != time_header:
                voltage = stats
                break

    domain = "unknown"
    if voltage and 20.0 <= abs(voltage["mean"]) <= 30.0 and (voltage.get("ripple_pct") or 0) < 8:
        domain = "dc_24v_scope"
    elif current and _mapped("ib"):
        domain = "ac_polyphase"
    elif current or voltage:
        domain = "scope_campaign"

    return {
        "filename": filename,
        "headers": table.headers,
        "mapping": mapping,
        "warnings": list(table.warnings),
        "samples": max((c["samples"] for c in channels.values()), default=0),
        "fs_hz": None if fs is None else round(fs, 1),
        "domain": domain,
        "channels": channels,
        "v_mean": None if voltage is None else voltage["mean"],
        "v_rms": None if voltage is None else voltage["rms"],
        "v_ripple_pct": None if voltage is None else voltage["ripple_pct"],
        "v_channel": None if voltage is None else voltage["name"],
        "i_rms": None if current is None else current["rms"],
        "i_mean": None if current is None else current["mean"],
        "i_channel": None if current is None else current["name"],
        "waveform": [] if voltage is None else voltage["waveform"],
        "current_waveform": [] if current is None else current["waveform"],
    }
