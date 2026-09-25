"""Compara campañas CSV con el valor de diseño de una plantilla."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from calculator.stats import summarize_csv
from calculator.templates import get_template, get_templates


def _f(params: dict[str, Any], key: str, default: float | None = None) -> float | None:
    if key not in params or params[key] in ("", None):
        return default
    try:
        return float(params[key])
    except (TypeError, ValueError):
        return default


def _b(params: dict[str, Any], key: str) -> bool:
    value = params.get(key, False)
    if isinstance(value, str):
        return value.lower() in {"1", "true", "on", "yes", "si", "sí"}
    return bool(value)


def _unbalance(ia: float, ib: float, ic: float) -> float | None:
    vals = [v for v in (ia, ib, ic) if v and v > 0]
    if len(vals) < 2:
        return None
    avg = sum(vals) / len(vals)
    if avg <= 0:
        return None
    return max(abs(v - avg) for v in vals) / avg * 100.0


def _pick_metric(template: dict[str, Any], before: dict[str, Any] | None, after: dict[str, Any] | None, params: dict[str, Any]) -> tuple[float | None, str]:
    campaign = after or before or {}
    metric = template["metric"]
    if metric == "v_mean":
        return campaign.get("v_mean"), "V media del CSV"
    if metric == "i_rms":
        value = campaign.get("i_rms")
        if value is None:
            value = _f(params, "i_rms_manual")
        return value, "I RMS"
    if metric == "power_factor":
        return _f(params, "fp_medido"), "factor de potencia declarado"
    if metric == "freq_hz":
        if campaign.get("domain") == "dc_24v_scope" or str(params.get("sistema") or "").startswith("24"):
            return campaign.get("v_mean"), "V media del bus DC"
        return campaign.get("fs_hz") or _f(params, "f_nom"), "frecuencia"
    if metric == "thdi":
        return _f(params, "thdi_medido"), "THDi declarado / de campaña"
    if metric == "icc_ka":
        return _f(params, "icc_sitio"), "Icc de sitio"
    if metric == "icw_ka":
        return _f(params, "icw_catalogo"), "Icw de catálogo"
    if metric == "delta_t":
        return _f(params, "delta_t_est"), "ΔT estimado"
    if metric == "unbalance_pct":
        return _unbalance(
            _f(params, "ia_decl", 0) or 0,
            _f(params, "ib_decl", 0) or 0,
            _f(params, "ic_decl", 0) or 0,
        ), "desequilibrio de fases"
    if metric == "in_rms":
        return campaign.get("i_rms"), "corriente de canal (aprox. In si hay un canal)"
    if metric == "ip":
        return _f(params, "ip_catalogo"), "IP de envolvente"
    if metric == "forma_score":
        order = {"1": 1, "2b": 2, "3b": 3, "4a": 4, "4b": 5}
        return float(order.get(str(params.get("forma_actual") or "2b"), 2)), "forma de separación"
    if metric == "delta_campaigns":
        if not before or not after:
            return None, "comparación entre campañas"
        eje = str(params.get("eje") or "tensión media")
        key = "v_mean"
        if "rizado" in eje:
            key = "v_ripple_pct"
        elif "corriente" in eje:
            key = "i_rms"
        elif "THDi" in eje:
            return _f(params, "thdi_medido"), "THDi declarado"
        b, a = before.get(key), after.get(key)
        if b is None or a is None or b == 0:
            return None, eje
        return (a - b) / abs(b) * 100.0, f"variación {eje}"
    return campaign.get("v_mean"), "magnitud principal"


def _design_value(template: dict[str, Any], params: dict[str, Any]) -> float | None:
    field = template.get("design_field")
    if not field:
        return None
    if field == "forma_objetivo":
        order = {"1": 1, "2b": 2, "3b": 3, "4a": 4, "4b": 5}
        return float(order.get(str(params.get("forma_objetivo") or "3b"), 3))
    if template.get("metric") == "freq_hz" and str(params.get("sistema") or "").startswith("24"):
        return 24.0
    return _f(params, field)


def _status(measured: float | None, design: float | None, tolerance_pct: float, metric: str) -> str:
    if measured is None:
        return "SIN_DATOS"
    if design is None:
        return "REVISAR"
    if metric == "delta_campaigns":
        if measured <= -abs(tolerance_pct):
            return "EN_LINEA"
        if measured < 0:
            return "REVISAR"
        return "ATENCION"
    if design == 0:
        return "REVISAR"
    # For limits where lower measured is better (ripple, thdi, delta_t, unbalance)
    lower_better = metric in {"thdi", "delta_t", "unbalance_pct"} or metric == "freq_hz"
    if metric == "icw_ka" or metric == "ip":
        return "EN_LINEA" if measured + 1e-9 >= design else "ATENCION"
    rel = abs(measured - design) / abs(design) * 100.0
    if lower_better and measured <= design:
        return "EN_LINEA"
    if rel <= tolerance_pct:
        return "EN_LINEA"
    if rel <= tolerance_pct * 2.5:
        return "REVISAR"
    return "ATENCION"


LABELS = {
    "EN_LINEA": "En línea con el prediseño",
    "REVISAR": "Conviene revisar",
    "ATENCION": "Priorizar una revisión",
    "SIN_DATOS": "El CSV no trae este dato; se usa el formulario",
}


def _suggestions(template: dict[str, Any], status: str, params: dict[str, Any], before: dict | None, after: dict | None) -> list[str]:
    tips = [template["voice"]]
    cid = template["id"]
    if cid == "T01" and (after or before):
        camp = after or before
        ripple = camp.get("v_ripple_pct")
        limit = _f(params, "ripple_max_pct", 2) or 2
        if ripple is not None and ripple > limit:
            tips.append(
                f"El rizado da {ripple:.2f} % frente a {limit:.1f} % de trabajo. Revisa Ilim, carga del rack y el acoplo DC del Gratten antes de tocar la envolvente."
            )
        else:
            tips.append("El bus se ve tranquilo. Es un buen punto para dejar constancia en el expediente TAN como condición de servicio 24 V.")
    if cid == "T05" and not _b(params, "carga_armonica"):
        tips.append("Si el THDi de trabajo supera el umbral, activa carga armónica en Diseño TAN: el prediseño suma pérdidas, nota RIC 04 y neutro más generoso.")
    if cid == "T13":
        tips.append(
            f"Forma {params.get('forma_actual')} → objetivo {params.get('forma_objetivo')}. Recalcular el prediseño no pinta la forma a mano: cambia redundancia, racks o criticidad y deja que run_design elija."
        )
    if cid == "T19":
        tips.append("Para el CSV de pañol, mapea CH1 a tensión (va). El alias por defecto del Monitor trata CH1 como corriente; esta calculadora no cae en esa trampa.")
    if cid == "T20" and before and after:
        tips.append("Guarda ambos CSV junto al informe: la 61439 agradece condiciones de servicio repetibles, no una foto suelta.")
    if cid in {"T06", "T07"}:
        tips.append("Icc/Icw no salen del osciloscopio. El valor de sitio y el de catálogo XL³ se conversan aquí para ver si la envolvente prevista cubre el número.")
    if cid == "T22":
        tips.append("Abre Diseño TAN con los kW y racks actualizados. Esta calculadora no pisa el proyecto: te deja el recálculo como decisión explícita.")
    if status == "SIN_DATOS":
        tips.append("Completa los campos del formulario: el CSV cubre lo que el scope vio; el prediseño cubre lo que el tablero debe declarar.")
    if len(tips) < 3:
        tips.append(
            "IEC 61439-1 y -2 brillan cuando dejas In, IP, forma y calentamiento escritos. Este informe es una brújula de prediseño para el CFT, lista para crecer cuando el expediente profesional lo pida."
        )
    return tips[:5]


def _chart_payload(before: dict | None, after: dict | None, measured: float | None, design: float | None, unit: str) -> dict[str, Any]:
    labels = []
    values = []
    if before and before.get("v_mean") is not None:
        labels.append("CSV anterior")
        values.append(before.get("v_mean"))
    if after and after.get("v_mean") is not None:
        labels.append("CSV nuevo")
        values.append(after.get("v_mean"))
    if measured is not None:
        labels.append("Magnitud de la plantilla")
        values.append(measured)
    if design is not None:
        labels.append("Valor de diseño")
        values.append(design)
    return {
        "labels": labels,
        "values": [None if v is None else round(float(v), 4) for v in values],
        "unit": unit,
        "wave_before": [] if not before else before.get("waveform") or [],
        "wave_after": [] if not after else after.get("waveform") or [],
    }


def list_templates() -> list[dict[str, Any]]:
    return [
        {
            "id": item["id"],
            "name": item["name"],
            "category": item["category"],
            "iec": item["iec"],
            "summary": item["summary"],
            "fields": item["fields"],
        }
        for item in get_templates()
    ]


def analyze(
    template_id: str,
    params: dict[str, Any],
    csv_before: str | None = None,
    name_before: str = "",
    csv_after: str | None = None,
    name_after: str = "",
) -> dict[str, Any]:
    template = get_template(template_id)
    before = summarize_csv(csv_before, name_before) if csv_before else None
    after = summarize_csv(csv_after, name_after) if csv_after else None
    measured, metric_label = _pick_metric(template, before, after, params)
    design = _design_value(template, params)
    status = _status(measured, design, float(template["tolerance_pct"]), template["metric"])
    abs_delta = None if measured is None or design is None else round(measured - design, 4)
    rel_delta = None
    if measured is not None and design not in (None, 0):
        rel_delta = round((measured - design) / abs(design) * 100.0, 2)

    unit = next((f.get("unit") or "" for f in template["fields"] if f["name"] == template.get("design_field")), "")
    run_id = datetime.now(timezone.utc).strftime("CL-%Y%m%d-%H%M%S-") + uuid4().hex[:6]
    campaign = after or before
    narrative = (
        f"{template['voice']} "
        f"Plantilla {template['id']}: {metric_label} "
        f"{'—' if measured is None else f'{measured:g}'} "
        f"frente a diseño {'—' if design is None else f'{design:g}'} {unit}. "
        f"{LABELS[status]}."
    )
    if campaign and campaign.get("domain") == "dc_24v_scope" and template["metric"] == "thdi":
        narrative += " El CSV de 24 VDC del Gratten documenta el bus del rack; el THDi de 3P+N se declara en el formulario o se toma del Monitor AHF."

    return {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "template": {
            "id": template["id"],
            "name": template["name"],
            "category": template["category"],
            "iec": template["iec"],
            "summary": template["summary"],
        },
        "status": status,
        "status_label": LABELS[status],
        "measured": measured if measured is None else round(float(measured), 4),
        "design": design if design is None else round(float(design), 4),
        "unit": unit,
        "metric_label": metric_label,
        "abs_delta": abs_delta,
        "rel_delta_pct": rel_delta,
        "params": params,
        "before": before,
        "after": after,
        "narrative": narrative,
        "suggestions": _suggestions(template, status, params, before, after),
        "charts": _chart_payload(before, after, measured, design, unit),
        "iec_note": (
            "IEC 61439-1 (reglas generales) e IEC 61439-2 (conjuntos de potencia) "
            "ordenan corriente asignada, IP, forma de separación, calentamiento y cortocircuito "
            "en un solo expediente de conjunto. Eso es exactamente lo que un tablero TAN de "
            "telecomunicaciones agradece: números declarados, no intuición de pasillo."
        ),
    }
