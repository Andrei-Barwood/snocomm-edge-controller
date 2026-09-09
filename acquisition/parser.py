"""Lectores de campañas: CSV de osciloscopio y JSON de medidor/central."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
from typing import Any

import numpy as np

CHANNEL_ALIASES: dict[str, tuple[str, ...]] = {
    "time": (
        "t", "time", "tiempo", "second", "seconds", "sec", "s",
        "ms", "timestamp", "x", "xaxis",
    ),
    "ia": (
        "ia", "i_a", "i1", "ch1", "channel1", "c1", "current_a",
        "corriente_a", "i(a)", "ia(a)",
    ),
    "ib": ("ib", "i_b", "i2", "ch2", "channel2", "c2", "current_b", "corriente_b"),
    "ic": ("ic", "i_c", "i3", "ch3", "channel3", "c3", "current_c", "corriente_c"),
    "in": ("in", "i_n", "i4", "ch4", "channel4", "c4", "ineutro", "neutral", "in(a)"),
    "va": ("va", "v_a", "v1", "u_a", "voltage_a", "tension_a", "ua"),
    "vb": ("vb", "v_b", "v2", "u_b", "voltage_b", "tension_b", "ub"),
    "vc": ("vc", "v_c", "v3", "u_c", "voltage_c", "tension_c", "uc"),
}

REGISTER_ALIASES: dict[str, tuple[str, ...]] = {
    "thdi": ("thdi", "thd_i", "thd", "thdc", "i_thd"),
    "i1_rms": ("i1_rms", "i1", "ifund", "i_fund", "irms1"),
    "h3_rms": ("h3_rms", "h3", "i3", "i_h3"),
    "h5_rms": ("h5_rms", "h5", "i5", "i_h5"),
    "h7_rms": ("h7_rms", "h7", "i7", "i_h7"),
    "in_rms": ("in_rms", "in", "i_n_rms", "neutral_rms"),
    "freq_est": ("freq", "frequency", "f", "freq_est", "hz"),
    "ia_rms": ("ia_rms", "i_a_rms", "irms_a"),
    "vdc": ("vdc", "v_dc", "udc", "dc_bus_v"),
    "idc": ("idc", "i_dc", "dc_current"),
}


def _norm(name: str) -> str:
    text = name.strip().lower()
    text = text.replace("á", "a").replace("é", "e").replace("í", "i")
    text = text.replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    return re.sub(r"[^a-z0-9]+", "", text)


def _alias_lookup(table: dict[str, tuple[str, ...]], header: str) -> str | None:
    key = _norm(header)
    for target, aliases in table.items():
        if key in {_norm(item) for item in aliases} or key == _norm(target):
            return target
    return None


def suggest_mapping(headers: list[str]) -> dict[str, str]:
    """Asocia encabezados de osciloscopio/central a canales internos."""
    mapping: dict[str, str] = {}
    for header in headers:
        channel = _alias_lookup(CHANNEL_ALIASES, header)
        if channel and channel not in mapping:
            mapping[channel] = header
    return mapping


def _detect_delimiter(sample: str) -> str:
    first = next((line for line in sample.splitlines() if line.strip() and not line.startswith("#")), "")
    if first.count(";") >= first.count(",") and first.count(";") >= first.count("\t"):
        if first.count(";") > 0:
            return ";"
    if first.count("\t") > first.count(","):
        return "\t"
    return ","


def _to_float(token: str) -> float:
    text = token.strip().replace(" ", "")
    if text.count(",") == 1 and text.count(".") == 0:
        text = text.replace(",", ".")
    elif text.count(",") > 0 and text.count(".") > 0:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    return float(text)


def _is_numeric_row(cells: list[str]) -> bool:
    parsed = 0
    for cell in cells:
        if not cell.strip():
            continue
        try:
            _to_float(cell)
            parsed += 1
        except ValueError:
            return False
    return parsed > 0


@dataclass
class ParsedTable:
    headers: list[str]
    columns: dict[str, np.ndarray]
    mapping: dict[str, str]
    delimiter: str
    skipped_rows: int
    warnings: list[str] = field(default_factory=list)

    def preview(self, rows: int = 5) -> list[dict[str, float]]:
        size = min(rows, min((len(col) for col in self.columns.values()), default=0))
        out = []
        for i in range(size):
            out.append({name: float(values[i]) for name, values in self.columns.items()})
        return out


def parse_csv(text: str, mapping: dict[str, str] | None = None) -> ParsedTable:
    raw = text.lstrip("\ufeff")
    lines = [line for line in raw.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if len(lines) < 2:
        raise ValueError("El CSV no tiene suficientes filas (encabezado + datos).")
    delimiter = _detect_delimiter("\n".join(lines[:8]))
    header = [cell.strip() for cell in lines[0].split(delimiter)]
    start = 1
    if start < len(lines) and not _is_numeric_row(lines[start].split(delimiter)):
        start += 1
    rows: list[list[float]] = []
    skipped = start
    for line in lines[start:]:
        cells = line.split(delimiter)
        if not _is_numeric_row(cells):
            skipped += 1
            continue
        values: list[float] = []
        usable = True
        for idx in range(len(header)):
            token = cells[idx] if idx < len(cells) else ""
            if token.strip() == "":
                values.append(float("nan"))
                continue
            try:
                values.append(_to_float(token))
            except ValueError:
                usable = False
                break
        if usable:
            rows.append(values)
    if not rows:
        raise ValueError("No se encontraron filas numéricas en el CSV.")
    matrix = np.asarray(rows, dtype=float)
    columns = {header[i]: matrix[:, i] for i in range(len(header)) if header[i]}
    auto = suggest_mapping(list(columns))
    chosen = mapping or auto
    warnings: list[str] = []
    if "time" not in chosen:
        warnings.append("Sin columna de tiempo; se usará el muestreo declarado o 12.8 kHz.")
    if not any(key in chosen for key in ("ia", "ib", "ic", "in")):
        warnings.append("No se detectó ninguna corriente. Indique el mapeo de columnas.")
    return ParsedTable(
        headers=list(columns),
        columns=columns,
        mapping=chosen,
        delimiter=delimiter,
        skipped_rows=skipped,
        warnings=warnings,
    )


def parse_json_campaign(payload: dict[str, Any]) -> tuple[ParsedTable | None, dict[str, float]]:
    """Acepta formas de onda, registros de central, o ambos."""
    registers_in = payload.get("registers") if isinstance(payload.get("registers"), dict) else payload
    registers: dict[str, float] = {}
    for key, value in (registers_in or {}).items():
        target = _alias_lookup(REGISTER_ALIASES, str(key))
        if target is None:
            continue
        try:
            registers[target] = float(value)
        except (TypeError, ValueError):
            continue

    wave_block = payload.get("channels") if isinstance(payload.get("channels"), dict) else payload
    headers: list[str] = []
    columns: dict[str, np.ndarray] = {}
    for key, value in (wave_block or {}).items():
        if key in {"registers", "source", "circuit", "fs", "filename", "mapping"}:
            continue
        if not isinstance(value, list) or not value:
            continue
        try:
            columns[str(key)] = np.asarray(value, dtype=float)
            headers.append(str(key))
        except (TypeError, ValueError):
            continue

    table = None
    if columns:
        mapping = payload.get("mapping") if isinstance(payload.get("mapping"), dict) else suggest_mapping(headers)
        table = ParsedTable(
            headers=headers,
            columns=columns,
            mapping={str(k): str(v) for k, v in mapping.items()},
            delimiter="json",
            skipped_rows=0,
        )
    return table, registers
