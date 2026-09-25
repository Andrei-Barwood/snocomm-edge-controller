"""Catálogo de CSV de demostración para el examen de titulación."""

from __future__ import annotations

from pathlib import Path
from typing import Any

EXAMPLES_DIR = Path(__file__).resolve().parent

CATALOG: list[dict[str, Any]] = [
    {
        "file": "demo_01_bus_24v_estable.csv",
        "title": "Bus 24 V estable",
        "template_id": "T01",
        "role": "CSV nuevo",
        "story": "Rack de telecomunicaciones en régimen. CH1 en el bus 24 VDC, rizado bajo.",
        "form": {"v_nom": 24, "ripple_max_pct": 2, "fuente": "wanptek KPS305D", "rack_id": "RACK-TEL-01"},
        "expect": "EN_LINEA",
    },
    {
        "file": "demo_02_bus_24v_rizado.csv",
        "title": "Bus 24 V con rizado de rectificador",
        "template_id": "T01",
        "role": "CSV nuevo",
        "story": "Mismo punto, fuente con rizado 120 Hz visible. Sirve para hablar de filtrado y condiciones de servicio.",
        "form": {"v_nom": 24, "ripple_max_pct": 2, "fuente": "rectificador de rack", "rack_id": "RACK-TEL-01"},
        "expect": "EN_LINEA o REVISAR según media; el rizado dispara la sugerencia T01",
    },
    {
        "file": "demo_03_bus_24v_caida.csv",
        "title": "Bus 24 V con caída de tensión",
        "template_id": "T01",
        "role": "CSV nuevo",
        "story": "Ilim corta o carga de rack excesiva: el bus se queda cerca de 21,4 V.",
        "form": {"v_nom": 24, "ripple_max_pct": 2, "fuente": "wanptek KPS305D", "rack_id": "RACK-AULA-02"},
        "expect": "ATENCION",
    },
    {
        "file": "demo_04_antes_ilim.csv",
        "title": "Antes del ajuste de Ilim",
        "template_id": "T20",
        "role": "CSV anterior",
        "pair": "demo_05_despues_ilim.csv",
        "story": "Campaña previa: 23,2 V y rizado. Se usa como CSV anterior en T20.",
        "form": {
            "mejora_min_pct": 10,
            "eje": "rizado",
            "intervencion": "subir Ilim y aliviar un rack",
            "mismo_punto": True,
        },
        "expect": "par T20",
    },
    {
        "file": "demo_05_despues_ilim.csv",
        "title": "Después del ajuste de Ilim",
        "template_id": "T20",
        "role": "CSV nuevo",
        "pair": "demo_04_antes_ilim.csv",
        "story": "Misma sonda, mismo bornes: bus a 24,0 V y rizado abajo. Eje de comparación: rizado.",
        "form": {
            "mejora_min_pct": 10,
            "eje": "rizado",
            "intervencion": "subir Ilim y aliviar un rack",
            "mismo_punto": True,
        },
        "expect": "EN_LINEA (el rizado baja)",
    },
    {
        "file": "demo_06_corriente_con_reserva.csv",
        "title": "Alimentador con reserva",
        "template_id": "T02",
        "role": "CSV nuevo",
        "story": "Ia ~ 50 A RMS frente a In 63 A. Hay reserva; el contraste abre la conversación de margen.",
        "form": {"in_diseno": 63, "margen_pct": 20, "num_racks": 4, "redundancia": "N+1"},
        "expect": "REVISAR",
    },
    {
        "file": "demo_07_corriente_justa.csv",
        "title": "Alimentador al límite de In",
        "template_id": "T02",
        "role": "CSV nuevo",
        "story": "Ia ~ 61 A RMS contra In 63 A. Reserva casi agotada: conversación de ampliar o repartir racks.",
        "form": {"in_diseno": 63, "margen_pct": 20, "num_racks": 6, "redundancia": "N"},
        "expect": "EN_LINEA o REVISAR (cerca del diseño)",
    },
    {
        "file": "demo_08_fases_desbalance.csv",
        "title": "Tres fases desequilibradas",
        "template_id": "T09",
        "role": "CSV nuevo",
        "story": "Export estilo central (no es captura 2 ch del Gratten). Ia/Ic cargadas, Ib liviana. Completar Ia/Ib/Ic del formulario con los RMS del informe.",
        "form": {"unbalance_max": 10, "ia_decl": 20, "ib_decl": 12, "ic_decl": 19},
        "expect": "ATENCION por desequilibrio",
    },
    {
        "file": "demo_09_gratten_ch1_ch2.csv",
        "title": "Gratten 2 canales: Vbus y corriente de rack",
        "template_id": "T19",
        "role": "CSV nuevo",
        "story": "CH1 ≈ 24 VDC, CH2 ≈ 1,2 A. Caso realista de pañol con los dos canales del GA1102CAL.",
        "form": {
            "v_nom": 24,
            "mapeo": "CH1 va / CH2 ia",
            "acoplo": "DC",
            "instrumento": "Gratten GA1102CAL",
        },
        "expect": "EN_LINEA en T19 / T01",
    },
]


def example_path(filename: str) -> Path:
    path = (EXAMPLES_DIR / filename).resolve()
    if path.parent != EXAMPLES_DIR or not path.is_file():
        raise FileNotFoundError(filename)
    return path
