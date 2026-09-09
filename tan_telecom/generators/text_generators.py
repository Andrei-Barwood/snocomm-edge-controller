"""Informes de texto: Markdown, HTML imprimible y CSV de la BOM."""

from __future__ import annotations

import csv
import html
from pathlib import Path
from typing import Any

from ..models import ProjectResult


def _extras_block(extras: dict[str, Any] | None) -> dict[str, Any]:
    return extras or {}


def generate_markdown(
    result: ProjectResult, output_path: Path, extras: dict[str, Any] | None = None
) -> Path:
    extras = _extras_block(extras)
    observed = extras.get("observed_harmonics") or {}
    lines = [
        f"# Informe TAN-Telecom — {result.project_id}",
        "",
        "Predimensionamiento académico. No certifica IEC 61439 ni sustituye la memoria RIC.",
        "",
        f"- Proyecto TAN: `{result.project_id}`",
        f"- Proyecto común: `{extras.get('shared_project_id') or '—'}`",
        f"- Generado (UTC): {result.generated_at}",
        f"- Familia: {result.separation.familia_tan} · Forma {result.separation.forma.value}",
        f"- Envolvente: {result.enclosure.codigo} · IP{result.enclosure.ip_seleccionado}",
        "",
        "## Entradas",
        "",
        f"| Parámetro | Valor |",
        f"|---|---|",
        f"| Potencia | {result.inputs.potencia_kw} kW |",
        f"| Racks | {result.inputs.num_racks} |",
        f"| Redundancia | {result.inputs.redundancia.value} |",
        f"| IP mínimo | IP{result.inputs.ip_minimo} |",
        f"| Carga armónica | {'Sí' if result.inputs.carga_armonica else 'No'} |",
        f"| Sísmico | {'Sí' if result.inputs.sismico else 'No'} |",
        "",
        "## Cálculo eléctrico",
        "",
        f"- Fórmula: `{result.electrical.formula_in}`",
        f"- In base: **{result.electrical.in_base_a} A**",
        f"- In selección: **{result.electrical.in_seleccion_a} A**",
        f"- Icc / Icw: {result.electrical.icc_estimada_ka} / {result.electrical.icw_requerida_ka} kA",
        f"- ΔT estimado: {result.electrical.delta_t_estimado_c} °C (límite {result.electrical.limite_delta_t_c} °C)",
        "",
        "## Monitor AHF → TAN",
        "",
    ]
    if observed:
        lines += [
            f"- THDi observado: {observed.get('thdi')} % ({observed.get('thdi_method') or 'académico'})",
            f"- I1 / H3 / H5 / H7: {observed.get('i1_rms')} / {observed.get('h3_rms')} / {observed.get('h5_rms')} / {observed.get('h7_rms')} A",
            f"- In RMS: {observed.get('in_rms')} A",
            f"- I compensación: {extras.get('compensation_current_a')} A",
            f"- {extras.get('ahf_module_suggestion') or ''}",
            f"- {extras.get('ric04_neutral_note') or ''}",
            "",
        ]
    else:
        lines += ["Sin telemetría DSP asociada a este informe.", ""]

    bank = extras.get("power_stage") or {}
    if bank:
        lines += [
            "## Banco 24 V",
            "",
            f"- Estado: {bank.get('state')} · Falla: {bank.get('fault')}",
            f"- Salidas físicas: {bank.get('physical_outputs_available')}",
            "",
        ]

    lines += ["## Verificaciones de diseño", "", "| N° | Característica | Artículo | Estado |", "|---:|---|---|---|"]
    for item in result.verifications:
        lines.append(
            f"| {item.numero} | {item.caracteristica} | {item.articulo} | {item.estado} |"
        )
    lines += ["", "## Lista de materiales", "", "| Código | Descripción | Cant. | Ud. | Categoría |", "|---|---|---:|---|---|"]
    for item in result.bom:
        lines.append(
            f"| {item.codigo} | {item.descripcion} | {item.cantidad} | {item.unidad} | {item.categoria} |"
        )
    if result.warnings:
        lines += ["", "## Advertencias", ""]
        lines += [f"- {w}" for w in result.warnings]
    lines += [
        "",
        "---",
        "Generado por TAN-Telecom. Entregable de preingeniería; no es sello TAN ni ensayo de tipo.",
        "",
    ]
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def generate_html(
    result: ProjectResult, output_path: Path, extras: dict[str, Any] | None = None
) -> Path:
    extras = _extras_block(extras)
    observed = extras.get("observed_harmonics") or {}
    warnings_html = "".join(f"<li>{html.escape(w)}</li>" for w in result.warnings)
    ver_rows = "".join(
        "<tr>"
        f"<td>{item.numero}</td><td>{html.escape(item.caracteristica)}</td>"
        f"<td>{html.escape(item.articulo)}</td><td>{html.escape(item.estado)}</td>"
        "</tr>"
        for item in result.verifications
    )
    bom_rows = "".join(
        "<tr>"
        f"<td>{html.escape(item.codigo)}</td><td>{html.escape(item.descripcion)}</td>"
        f"<td>{item.cantidad}</td><td>{html.escape(item.unidad)}</td>"
        f"<td>{html.escape(item.categoria)}</td>"
        "</tr>"
        for item in result.bom
    )
    observed_html = (
        f"<p>THDi {html.escape(str(observed.get('thdi')))} % · "
        f"I compensación {html.escape(str(extras.get('compensation_current_a')))} A</p>"
        f"<p>{html.escape(str(extras.get('ahf_module_suggestion') or ''))}</p>"
        f"<p>{html.escape(str(extras.get('ric04_neutral_note') or ''))}</p>"
        if observed
        else "<p>Sin telemetría DSP asociada.</p>"
    )
    document = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Informe TAN-Telecom {html.escape(result.project_id)}</title>
  <style>
    body {{ font: 15px/1.45 system-ui, sans-serif; color: #303030; max-width: 960px; margin: 32px auto; padding: 0 20px; }}
    h1, h2 {{ letter-spacing: -0.03em; }}
    .meta {{ color: #626975; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 24px; }}
    th, td {{ border: 1px solid #bcc7d6; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #303030; color: #fff; }}
    tr:nth-child(even) td {{ background: #f5f7fa; }}
    .warn {{ background: #fff9e7; border-left: 5px solid #CCB244; padding: 10px 14px; }}
    @media print {{ a {{ color: inherit; text-decoration: none; }} }}
  </style>
</head>
<body>
  <p class="meta">TAN-Telecom · predimensionamiento académico IEC 61439 / RIC</p>
  <h1>Informe de tablero {html.escape(result.project_id)}</h1>
  <p>Proyecto común: {html.escape(str(extras.get('shared_project_id') or '—'))} · {html.escape(result.generated_at)}</p>
  <p><strong>{html.escape(result.enclosure.nombre)}</strong> · Familia {html.escape(result.separation.familia_tan)} · Forma {html.escape(result.separation.forma.value)} · IP{html.escape(str(result.enclosure.ip_seleccionado))}</p>
  <h2>Cálculo</h2>
  <p>In base {result.electrical.in_base_a} A · selección {result.electrical.in_seleccion_a} A · Icc {result.electrical.icc_estimada_ka} kA · ΔT {result.electrical.delta_t_estimado_c} °C</p>
  <h2>Monitor AHF</h2>
  {observed_html}
  <h2>Verificaciones de diseño</h2>
  <table><thead><tr><th>N°</th><th>Característica</th><th>Artículo</th><th>Estado</th></tr></thead><tbody>{ver_rows}</tbody></table>
  <h2>Lista de materiales</h2>
  <table><thead><tr><th>Código</th><th>Descripción</th><th>Cant.</th><th>Ud.</th><th>Categoría</th></tr></thead><tbody>{bom_rows}</tbody></table>
  {"<div class='warn'><h2>Advertencias</h2><ul>" + warnings_html + "</ul></div>" if result.warnings else ""}
  <p class="meta">No sustituye ensayos, memoria RIC ni certificación TAN del fabricante/ensamblador.</p>
</body>
</html>
"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    return output_path


def generate_bom_csv(result: ProjectResult, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["proyecto", "codigo", "descripcion", "cantidad", "unidad", "categoria", "observaciones"]
        )
        for item in result.bom:
            writer.writerow(
                [
                    result.project_id,
                    item.codigo,
                    item.descripcion,
                    item.cantidad,
                    item.unidad,
                    item.categoria,
                    item.observaciones,
                ]
            )
    return output_path
