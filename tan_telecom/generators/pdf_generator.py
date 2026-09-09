"""
Generador PDF resumen técnico (fpdf2) para TAN-Telecom.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from fpdf import FPDF

from ..models import ProjectResult


def _safe(text: object) -> str:
    """Normaliza texto a Latin-1 compatible con fuentes core de fpdf2."""
    replacements = {
        "—": "-",
        "–": "-",
        "≥": ">=",
        "≤": "<=",
        "√": "sqrt",
        "φ": "phi",
        "η": "eta",
        "Δ": "d",
        "°": " deg",
        "³": "3",
        "·": ".",
        "“": '"',
        "”": '"',
        "’": "'",
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
        "Á": "A",
        "É": "E",
        "Í": "I",
        "Ó": "O",
        "Ú": "U",
        "Ñ": "N",
        "ü": "u",
        "Ü": "U",
    }
    out = str(text)
    for a, b in replacements.items():
        out = out.replace(a, b)
    return out.encode("latin-1", errors="replace").decode("latin-1")


class TanTelecomPDF(FPDF):
    """PDF con encabezado y pie de página corporativos."""

    def header(self) -> None:
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(31, 78, 121)
        self.set_x(self.l_margin)
        self.cell(0, 8, _safe("TAN-Telecom | Tableros TAN para telecomunicaciones"), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(31, 78, 121)
        self.set_line_width(0.4)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(4)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(90, 90, 90)
        self.set_x(self.l_margin)
        self.cell(
            0,
            8,
            _safe(
                f"IEC 61439-1 & 2 | Ref. XL3/TAN | {datetime.now():%Y-%m-%d} | Pag. {self.page_no()}/{{nb}}"
            ),
            align="C",
        )


def _kv(pdf: FPDF, key: str, value: object, key_w: float = 55) -> None:
    """Escribe un par clave/valor ocupando el ancho útil de página."""
    pdf.set_x(pdf.l_margin)
    usable = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(key_w, 6, _safe(f"{key}:"))
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(usable - key_w, 6, _safe(str(value)))


def _section(pdf: FPDF, title: str) -> None:
    pdf.ln(2)
    pdf.set_x(pdf.l_margin)
    pdf.set_fill_color(31, 78, 121)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)
    usable = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.cell(usable, 8, _safe(title), new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)


def generate_pdf(
    result: ProjectResult,
    output_path: Path,
    extras: dict[str, Any] | None = None,
) -> Path:
    """
    Genera un PDF resumen de 2-3 páginas.

    Args:
        result: Resultado de diseño.
        output_path: Ruta del archivo .pdf.

    Returns:
        Ruta del archivo generado.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pdf = TanTelecomPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    usable = pdf.w - pdf.l_margin - pdf.r_margin

    # Portada / título
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(31, 78, 121)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(usable, 9, _safe("Resumen Tecnico de Configuracion"))
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(usable, 6, _safe(f"Proyecto: {result.project_id}"))
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(usable, 6, _safe(f"Familia: {result.separation.familia_tan}"))
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(usable, 6, _safe(f"Generado (UTC): {result.generated_at}"))

    _section(pdf, "1. Parametros de entrada")
    for k, v in [
        ("Potencia instalada", f"{result.inputs.potencia_kw} kW"),
        ("Numero de racks", str(result.inputs.num_racks)),
        ("Redundancia", result.inputs.redundancia.value),
        ("IP minimo", f"IP{result.inputs.ip_minimo}"),
        ("Carga armonica", "Si" if result.inputs.carga_armonica else "No"),
        ("Sismico", "Si" if result.inputs.sismico else "No"),
        (
            "Tension / cos phi / eta",
            f"{result.inputs.tension_v} V / {result.inputs.cos_phi} / {result.inputs.rendimiento}",
        ),
    ]:
        _kv(pdf, k, v)

    _section(pdf, "2. Resultados de calculo")
    for k, v in [
        ("Formula In", result.electrical.formula_in),
        ("In base", f"{result.electrical.in_base_a} A"),
        ("Factor redundancia", str(result.electrical.factor_redundancia)),
        ("In diseno", f"{result.electrical.in_diseno_a} A"),
        ("In seleccion", f"{result.electrical.in_seleccion_a} A"),
        (
            "Icc / Icw",
            f"{result.electrical.icc_estimada_ka} / {result.electrical.icw_requerida_ka} kA",
        ),
        ("RDF", str(result.electrical.rdf)),
        (
            "Simultaneidad / Utilizacion",
            f"{result.electrical.factor_simultaneidad} / {result.electrical.factor_utilizacion}",
        ),
        ("P disipada", f"{result.electrical.potencia_disipada_w} W"),
        (
            "dT estimado",
            f"{result.electrical.delta_t_estimado_c} degC (limite {result.electrical.limite_delta_t_c})",
        ),
        ("Calentamiento", "OK" if result.electrical.calentamiento_ok else "REVISAR"),
    ]:
        _kv(pdf, k, v)

    # Página 2 — recomendaciones
    pdf.add_page()
    _section(pdf, "3. Envolvente y forma de separacion")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(
        usable,
        7,
        _safe(
            f"Envolvente: {result.enclosure.nombre} ({result.enclosure.codigo}) | "
            f"IP{result.enclosure.ip_seleccionado} | Forma {result.separation.forma.value}"
        ),
    )
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(
        usable,
        6,
        _safe(
            f"Imax {result.enclosure.corriente_max_a} A | "
            f"Icw/Icc {result.enclosure.icw_ka}/{result.enclosure.icc_ka} kA | "
            f"Criticidad: {result.separation.criticidad}"
        ),
    )

    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 6, _safe("Justificacion de envolvente:"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for line in result.enclosure.justificacion:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(usable, 5, _safe(f"- {line}"))

    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 6, _safe("Justificacion de forma de separacion:"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for line in result.separation.justificacion:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(usable, 5, _safe(f"- {line}"))

    _section(pdf, "4. Verificaciones criticas (resumen)")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(46, 117, 182)
    pdf.set_text_color(255, 255, 255)
    col_w = [12, 78, 22, usable - 12 - 78 - 22]
    headers = ["N", "Caracteristica", "Art.", "Estado"]
    pdf.set_x(pdf.l_margin)
    for w, h in zip(col_w, headers):
        pdf.cell(w, 7, _safe(h), border=1, fill=True)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 7)

    criticos = {2, 5, 9, 10, 11, 13, 14}
    for item in result.verifications:
        if item.numero not in criticos:
            continue
        car = item.caracteristica
        if len(car) > 52:
            car = car[:49] + "..."
        est = item.estado
        if len(est) > 38:
            est = est[:35] + "..."
        pdf.set_x(pdf.l_margin)
        pdf.cell(col_w[0], 6, str(item.numero), border=1)
        pdf.cell(col_w[1], 6, _safe(car), border=1)
        pdf.cell(col_w[2], 6, _safe(item.articulo), border=1)
        pdf.cell(col_w[3], 6, _safe(est), border=1)
        pdf.ln()

    extras = extras or {}
    if extras.get("observed_harmonics") or extras.get("shared_project_id"):
        _section(pdf, "5. Proyecto comun (Monitor AHF / Banco)")
        observed = extras.get("observed_harmonics") or {}
        for k, v in [
            ("Proyecto comun", extras.get("shared_project_id") or "-"),
            ("THDi observado", observed.get("thdi", "sin datos")),
            ("I compensacion [A]", extras.get("compensation_current_a", "-")),
            ("Sugerencia AHF", extras.get("ahf_module_suggestion") or "-"),
            ("RIC 04 neutro", extras.get("ric04_neutral_note") or "-"),
        ]:
            _kv(pdf, k, v)

    if result.warnings:
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(160, 0, 0)
        pdf.set_x(pdf.l_margin)
        pdf.cell(0, 6, _safe("Advertencias:"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(0, 0, 0)
        for wmsg in result.warnings:
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(usable, 5, _safe(f"- {wmsg}"))

    pdf.ln(6)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(
        usable,
        5,
        _safe(
            "Documento generado automaticamente por TAN-Telecom. "
            "Predimensionamiento academico/profesional de apoyo; no sustituye "
            "ensayos de laboratorio, memoria de calculo de instalacion ni "
            "certificacion TAN del fabricante/ensamblador."
        ),
    )

    pdf.output(str(output_path))
    return output_path
