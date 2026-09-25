"""Genera los CSV de demostración del examen. Ejecutar: python -m calculator.examples.generate"""

from __future__ import annotations

from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def _gratten_header(channel: str, coupling: str, note: str) -> str:
    return (
        "# GRATTEN GA1102CAL DIGITAL STORAGE OSCILLOSCOPE\n"
        f"# Channel: {channel}\n"
        f"# Coupling: {coupling}\n"
        "# Probe: 1X\n"
        "# Demo examen de titulacion CFT Paillaco · Snocomm\n"
        f"# {note}\n"
    )


def _write(name: str, header: str, columns: list[str], *series: np.ndarray) -> None:
    path = HERE / name
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(header)
        fh.write(",".join(columns) + "\n")
        for row in zip(*series):
            fh.write(",".join(f"{value:.6f}" for value in row) + "\n")
    print(f"wrote {path.name} ({series[0].size} samples)")


def _time(n: int, fs: float) -> np.ndarray:
    return (np.arange(n) - n // 2) / fs


def main() -> None:
    rng = np.random.default_rng(61439)

    fs_dc = 2000.0
    n_dc = 400
    t_dc = _time(n_dc, fs_dc)

    estable = 24.00 + 0.025 * np.sin(2 * np.pi * 50 * t_dc) + rng.normal(0, 0.012, n_dc)
    _write(
        "demo_01_bus_24v_estable.csv",
        _gratten_header("CH1", "DC", "Bus 24 VDC estable. Plantilla T01. Valor de diseno 24 V."),
        ["Time", "CH1"],
        t_dc,
        estable,
    )

    rizado = 24.00 + 1.15 * np.sin(2 * np.pi * 120 * t_dc) + rng.normal(0, 0.02, n_dc)
    _write(
        "demo_02_bus_24v_rizado.csv",
        _gratten_header("CH1", "DC", "Bus 24 V con rizado 120 Hz. Plantilla T01. ripple_max 2 %."),
        ["Time", "CH1"],
        t_dc,
        rizado,
    )

    caida = 21.40 + 0.08 * np.sin(2 * np.pi * 120 * t_dc) + rng.normal(0, 0.03, n_dc)
    _write(
        "demo_03_bus_24v_caida.csv",
        _gratten_header("CH1", "DC", "Caida de bus ~21.4 V. Plantilla T01. Esperado: ATENCION."),
        ["Time", "CH1"],
        t_dc,
        caida,
    )

    antes = 23.15 + 0.55 * np.sin(2 * np.pi * 120 * t_dc) + rng.normal(0, 0.04, n_dc)
    _write(
        "demo_04_antes_ilim.csv",
        _gratten_header("CH1", "DC", "T20 CSV anterior: Ilim corta, 23.2 V. Parear con demo_05."),
        ["Time", "CH1"],
        t_dc,
        antes,
    )

    despues = 24.02 + 0.03 * np.sin(2 * np.pi * 50 * t_dc) + rng.normal(0, 0.01, n_dc)
    _write(
        "demo_05_despues_ilim.csv",
        _gratten_header("CH1", "DC", "T20 CSV nuevo: mismo punto tras ajustar Ilim, 24.0 V."),
        ["Time", "CH1"],
        t_dc,
        despues,
    )

    fs_ac = 12800.0
    n_ac = 512
    t_ac = np.arange(n_ac) / fs_ac
    w = 2 * np.pi * 50.0 * t_ac
    ia_reserva = 50.0 * np.sqrt(2) * np.sin(w) + rng.normal(0, 0.15, n_ac)
    _write(
        "demo_06_corriente_con_reserva.csv",
        "# Campana de corriente de alimentador (sintetica 50 Hz).\n"
        "# No es captura 3P+N del Gratten (2 canales). Plantilla T02. In diseno 63 A.\n"
        "# Ia ~ 50 A RMS: hay reserva, el prediseño pide revision de margen.\n",
        ["Time", "Ia"],
        t_ac,
        ia_reserva,
    )

    ia_justa = 61.0 * np.sqrt(2) * np.sin(w) + rng.normal(0, 0.2, n_ac)
    _write(
        "demo_07_corriente_justa.csv",
        "# Campana de corriente cerca de In = 63 A. Plantilla T02.\n"
        "# Reserva casi agotada: conversacion de ampliar o redistribuir racks.\n",
        ["Time", "Ia"],
        t_ac,
        ia_justa,
    )

    ia = 20.0 * np.sqrt(2) * np.sin(w) + rng.normal(0, 0.1, n_ac)
    ib = 12.0 * np.sqrt(2) * np.sin(w - 2 * np.pi / 3) + rng.normal(0, 0.1, n_ac)
    ic = 19.0 * np.sqrt(2) * np.sin(w + 2 * np.pi / 3) + rng.normal(0, 0.1, n_ac)
    _write(
        "demo_08_fases_desbalance.csv",
        "# Tres corrientes de fase (sintetico). El Gratten GA1102CAL no captura 3P a la vez.\n"
        "# Plantilla T09. Formulario: Ia 20 A, Ib 12 A, Ic 19 A, desequilibrio max 10 %.\n",
        ["Time", "Ia", "Ib", "Ic"],
        t_ac,
        ia,
        ib,
        ic,
    )

    i_rack = 1.20 + 0.04 * np.sin(2 * np.pi * 120 * t_dc) + rng.normal(0, 0.008, n_dc)
    _write(
        "demo_09_gratten_ch1_ch2.csv",
        _gratten_header(
            "CH1=Va, CH2=Ia",
            "DC",
            "Dump de 2 canales ya mapeado: Va=CH1 bus 24 V, Ia=CH2 ~1.2 A. Plantilla T19 o T01.",
        ),
        ["Time", "Va", "Ia"],
        t_dc,
        estable,
        i_rack,
    )


if __name__ == "__main__":
    main()
