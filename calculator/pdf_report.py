"""Informe PDF de la calculadora, con gráficos de barras dibujados en fpdf2."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from fpdf import FPDF


def _safe(text: object) -> str:
    replacements = {
        "—": "-", "–": "-", "≥": ">=", "≤": "<=", "Δ": "d", "°": " deg",
        "³": "3", "·": ".", "“": '"', "”": '"', "’": "'",
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ñ": "N",
        "ü": "u", "Ü": "U",
    }
    out = str(text)
    for a, b in replacements.items():
        out = out.replace(a, b)
    return out.encode("latin-1", errors="replace").decode("latin-1")


class CalculatorPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(48, 48, 48)
        self.cell(0, 8, _safe("Snocomm Energy Control  |  Calculadora comparativa IEC 61439"), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(227, 202, 117)
        self.set_line_width(0.6)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(4)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(90, 90, 90)
        self.cell(
            0,
            8,
            _safe(f"Andres Barbudo Rodriguez  ·  CFT Paillaco  ·  {datetime.now():%Y-%m-%d}  ·  Pag. {self.page_no()}/{{nb}}"),
            align="C",
        )


def _heading(pdf: CalculatorPDF, text: str) -> None:
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(72, 81, 153)
    pdf.cell(0, 8, _safe(text), new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(48, 48, 48)


def _para(pdf: CalculatorPDF, text: str) -> None:
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, _safe(text))
    pdf.ln(1)


def _kv(pdf: CalculatorPDF, rows: list[tuple[str, str]]) -> None:
    key_w = 48
    val_w = pdf.epw - key_w
    for key, value in rows:
        y = pdf.get_y()
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_xy(pdf.l_margin, y)
        pdf.multi_cell(key_w, 6, _safe(key))
        y_key = pdf.get_y()
        pdf.set_font("Helvetica", "", 10)
        pdf.set_xy(pdf.l_margin + key_w, y)
        pdf.multi_cell(val_w, 6, _safe(value))
        pdf.set_y(max(y_key, pdf.get_y()))


def _bars(pdf: CalculatorPDF, labels: list[str], values: list[float], unit: str) -> None:
    usable = [(lab, float(val)) for lab, val in zip(labels, values) if val is not None]
    if not usable:
        return
    peak = max(abs(v) for _, v in usable) or 1.0
    x0 = pdf.l_margin
    width = pdf.epw
    bar_h = 8
    pdf.set_font("Helvetica", "", 9)
    colors = [(72, 81, 153), (227, 202, 117), (48, 48, 48), (143, 50, 50)]
    for i, (lab, val) in enumerate(usable):
        y = pdf.get_y()
        if y > 270:
            pdf.add_page()
            y = pdf.get_y()
        pdf.set_fill_color(*colors[i % len(colors)])
        bw = max(4.0, width * 0.62 * abs(val) / peak)
        pdf.rect(x0, y, bw, bar_h, style="F")
        pdf.set_xy(x0 + bw + 3, y)
        pdf.cell(0, bar_h, _safe(f"{lab}: {val:g} {unit}"))
        pdf.ln(bar_h + 2)


def _waves(pdf: CalculatorPDF, before: list[float], after: list[float]) -> None:
    series = [("CSV anterior", before, (72, 81, 153)), ("CSV nuevo", after, (204, 178, 68))]
    series = [(n, w, c) for n, w, c in series if w]
    if not series:
        return
    height = 32
    width = pdf.epw
    y0 = pdf.get_y()
    if y0 + height > 275:
        pdf.add_page()
        y0 = pdf.get_y()
    pdf.set_draw_color(188, 199, 214)
    pdf.rect(pdf.l_margin, y0, width, height)
    all_v = [v for _, w, _ in series for v in w]
    vmin, vmax = min(all_v), max(all_v)
    span = (vmax - vmin) or 1.0
    for _, wave, color in series:
        pdf.set_draw_color(*color)
        pdf.set_line_width(0.35)
        n = max(1, len(wave) - 1)
        pts = []
        for i, val in enumerate(wave):
            x = pdf.l_margin + width * i / n
            y = y0 + height - (val - vmin) / span * (height - 4) - 2
            pts.append((x, y))
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            pdf.line(x1, y1, x2, y2)
    pdf.set_y(y0 + height + 4)


def render_pdf(result: dict[str, Any], dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    pdf = CalculatorPDF(format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    tpl = result["template"]
    _heading(pdf, tpl["name"])
    _para(pdf, f"{tpl['id']}  ·  {tpl['category']}  ·  {tpl['iec']}")
    _kv(
        pdf,
        [
            ("Informe", result["run_id"]),
            ("Estado", result["status_label"]),
            ("Medido", f"{result['measured']} {result.get('unit') or ''}" if result["measured"] is not None else "sin dato en CSV"),
            ("Diseno", f"{result['design']} {result.get('unit') or ''}" if result["design"] is not None else "sin dato de formulario"),
            ("Desvio", f"{result['abs_delta']}  ({result['rel_delta_pct']} %)" if result["abs_delta"] is not None else "-"),
        ],
    )
    pdf.ln(2)
    _heading(pdf, "Lectura")
    _para(pdf, result["narrative"])
    _heading(pdf, "Por que conviene la IEC 61439-1 y -2")
    _para(pdf, result["iec_note"])
    _heading(pdf, "Comparacion grafica")
    charts = result.get("charts") or {}
    _bars(pdf, charts.get("labels") or [], charts.get("values") or [], charts.get("unit") or "")
    if charts.get("wave_before") or charts.get("wave_after"):
        _heading(pdf, "Forma de onda (muestreo del CSV)")
        _waves(pdf, charts.get("wave_before") or [], charts.get("wave_after") or [])
    _heading(pdf, "Sugerencias")
    for tip in result.get("suggestions") or []:
        _para(pdf, f"- {tip}")

    def _campaign(title: str, camp: dict[str, Any] | None) -> None:
        if not camp:
            return
        _heading(pdf, title)
        _kv(
            pdf,
            [
                ("Archivo", camp.get("filename") or "-"),
                ("Dominio", camp.get("domain") or "-"),
                ("Muestras", str(camp.get("samples") or "-")),
                ("fs", f"{camp.get('fs_hz')} Hz" if camp.get("fs_hz") else "-"),
                ("V media", str(camp.get("v_mean") if camp.get("v_mean") is not None else "-")),
                ("Rizado", f"{camp.get('v_ripple_pct')} %" if camp.get("v_ripple_pct") is not None else "-"),
                ("I RMS", str(camp.get("i_rms") if camp.get("i_rms") is not None else "-")),
                ("Canales", ", ".join(camp.get("headers") or [])),
            ],
        )

    _campaign("CSV anterior", result.get("before"))
    _campaign("CSV nuevo", result.get("after"))
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(
        0,
        4,
        _safe(
            "Informe de prediseño Snocomm. Marco legal, autorizaciones y validez comercial: pestaña Legislación de la aplicación."
        ),
    )
    dest = Path(dest)
    pdf.output(str(dest))
    return dest
