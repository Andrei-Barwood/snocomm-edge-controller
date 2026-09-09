#!/usr/bin/env python3
"""Carta Gantt del TPA — versión de comunicación (etapas e hitos)."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

OUT_DIR = Path(__file__).resolve().parent
PDF_PATH = OUT_DIR / "CARTA_GANTT_TPA_COMUNICACION.pdf"
LOGO_PATH = OUT_DIR / "assets_gantt" / "cft_logo.png"
CLASS_COPY = Path(
    "/Users/andreibarwood/Documents/CFT/2026/02 - Semestre 2/01 - TPA"
    "/06 - 28 de agosto/Carta_Gantt_TPA_Comunicacion.pdf"
)

INK = HexColor("#2C2C2C")
GRAPHITE = HexColor("#4A4A4A")
MUTED = HexColor("#6B6B6B")
LINE = HexColor("#D0D5DC")
BG = HexColor("#F4F6F8")
NAVY = HexColor("#1B4F9C")
NAVY_DEEP = HexColor("#123A75")
ORANGE = HexColor("#F39200")
ORANGE_DEEP = HexColor("#D97A00")
GREEN = HexColor("#7AB51D")
OK = HexColor("#3D7A5A")
PLAN = HexColor("#C5CED9")
PAPER = HexColor("#F7F8FA")

PROJECT_START = date(2026, 6, 8)
STATUS = date(2026, 8, 28)
N_WEEKS = 26
PROJECT_END = PROJECT_START + timedelta(weeks=N_WEEKS) - timedelta(days=1)

ETAPAS = [
    {
        "id": "E1",
        "name": "Diagnóstico del problema y planificación",
        "start": 1,
        "finish": 4,
        "pct": 100,
    },
    {
        "id": "E2",
        "name": "Organización de la solución",
        "start": 2,
        "finish": 6,
        "pct": 100,
    },
    {
        "id": "E3",
        "name": "Cálculo y documentación del tablero",
        "start": 3,
        "finish": 8,
        "pct": 100,
    },
    {
        "id": "E4",
        "name": "Estudio de las corrientes no deseadas",
        "start": 5,
        "finish": 10,
        "pct": 100,
    },
    {
        "id": "E5",
        "name": "Preparación de la demostración",
        "start": 7,
        "finish": 11,
        "pct": 100,
    },
    {
        "id": "E6",
        "name": "Prueba segura en laboratorio",
        "start": 10,
        "finish": 11,
        "pct": 100,
    },
    {
        "id": "E7",
        "name": "Recolección de evidencias y resultados",
        "start": 11,
        "finish": 18,
        "pct": 51,
    },
    {
        "id": "E8",
        "name": "Informe escrito y defensa oral",
        "start": 13,
        "finish": 26,
        "pct": 47,
    },
]

HITOS = [
    {
        "id": "H1",
        "name": "Alcance del proyecto acordado",
        "week": 2,
        "date": date(2026, 6, 21),
        "significado": "Quedó por escrito el problema, lo que se entrega y lo que queda fuera.",
        "comunica": "Documento de acuerdos",
    },
    {
        "id": "H2",
        "name": "Propuesta de tablero lista",
        "week": 7,
        "date": date(2026, 7, 26),
        "significado": "El cálculo del tablero se puede mostrar con planilla y un resumen.",
        "comunica": "Planilla y resumen en PDF",
    },
    {
        "id": "H3",
        "name": "Estudio de las corrientes validado",
        "week": 10,
        "date": date(2026, 8, 16),
        "significado": "El problema se explica con ejemplos de prueba, no con un medidor certificado.",
        "comunica": "Demostración en pantalla",
    },
    {
        "id": "H4",
        "name": "Demostración lista para mostrar",
        "week": 11,
        "date": date(2026, 8, 21),
        "significado": "Hay una pantalla con tres vistas para mostrar el proyecto a distintas personas.",
        "comunica": "Prototipo en tres vistas",
    },
    {
        "id": "H5",
        "name": "Prueba segura de laboratorio",
        "week": 11,
        "date": date(2026, 8, 21),
        "significado": "Se prueba a baja tensión, con parada de emergencia, sin conectar a la red.",
        "comunica": "Protocolo de laboratorio",
    },
    {
        "id": "H6",
        "name": "Evidencias del trabajo reunidas",
        "week": 11,
        "date": date(2026, 8, 23),
        "significado": "Quedó documentado lo que sí se demostró y cuáles son los límites.",
        "comunica": "Informe de evidencias",
    },
    {
        "id": "H7",
        "name": "Borrador del informe escrito",
        "week": 11,
        "date": date(2026, 8, 23),
        "significado": "El informe escrito está armado para la revisión del profesor guía.",
        "comunica": "Informe escrito (memoria)",
    },
    {
        "id": "H8",
        "name": "Defensa oral del proyecto",
        "week": 26,
        "date": date(2026, 12, 4),
        "significado": "Presentación oral del proyecto ante la comisión.",
        "comunica": "Oratoria y defensa",
    },
]

MONTHS = [
    ("JUN", 1, 3),
    ("JUL", 4, 8),
    ("AGO", 9, 12),
    ("SEP", 13, 17),
    ("OCT", 18, 21),
    ("NOV", 22, 25),
    ("DIC", 26, 26),
]


def week_start(week: int) -> date:
    return PROJECT_START + timedelta(weeks=week - 1)


def week_end(week: int) -> date:
    return week_start(week) + timedelta(days=6)


def fmt(d: date) -> str:
    months = "ene feb mar abr may jun jul ago sep oct nov dic".split()
    return f"{d.day:02d}-{months[d.month - 1]}-{d.year}"


def fmt_long(d: date) -> str:
    months = (
        "enero febrero marzo abril mayo junio julio agosto "
        "septiembre octubre noviembre diciembre"
    ).split()
    return f"{d.day} de {months[d.month - 1]} de {d.year}"


def global_progress() -> int:
    num = sum((r["finish"] - r["start"] + 1) * r["pct"] for r in ETAPAS)
    den = sum(r["finish"] - r["start"] + 1 for r in ETAPAS)
    return round(num / den)


def register_fonts() -> tuple[str, str]:
    candidates = [
        (
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ),
        ("/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"),
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
    ]
    for regular, bold in candidates:
        if Path(regular).exists() and Path(bold).exists():
            pdfmetrics.registerFont(TTFont("Body", regular))
            pdfmetrics.registerFont(TTFont("Body-Bold", bold))
            return "Body", "Body-Bold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_B = register_fonts()


def wrap(c: canvas.Canvas, text: str, font: str, size: float, max_w: float) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else f"{cur} {word}"
        if c.stringWidth(trial, font, size) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def diamond(c: canvas.Canvas, x: float, y: float, s: float, fill: Color) -> None:
    p = c.beginPath()
    p.moveTo(x, y + s)
    p.lineTo(x + s, y)
    p.lineTo(x, y - s)
    p.lineTo(x - s, y)
    p.close()
    c.setFillColor(fill)
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.drawPath(p, fill=1, stroke=1)


def week_x(chart_x: float, chart_w: float, week: float) -> float:
    return chart_x + (week - 1) * (chart_w / N_WEEKS)


def draw_header(c: canvas.Canvas, w: float, h: float, page: str) -> float:
    header_h = 32 * mm
    c.setFillColor(white)
    c.rect(0, h - header_h, w, header_h, fill=1, stroke=0)
    c.setFillColor(ORANGE)
    c.rect(0, h - header_h, w, 2.2 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY_DEEP)
    c.rect(0, h - header_h - 1.6 * mm, w, 1.6 * mm, fill=1, stroke=0)

    if LOGO_PATH.exists():
        logo_h = 16 * mm
        logo_w = logo_h * (302 / 167)
        c.drawImage(
            str(LOGO_PATH),
            12 * mm,
            h - 26.5 * mm,
            width=logo_w,
            height=logo_h,
            mask="auto",
            preserveAspectRatio=True,
        )
        title_x = 12 * mm + logo_w + 8 * mm
    else:
        title_x = 12 * mm

    c.setFillColor(NAVY_DEEP)
    c.setFont(FONT_B, 13)
    c.drawString(title_x, h - 13 * mm, "Carta Gantt del Trabajo Práctico Aplicado")
    c.setFillColor(GRAPHITE)
    c.setFont(FONT, 8.4)
    c.drawString(
        title_x,
        h - 19 * mm,
        "Versión de comunicación  ·  solo etapas e hitos  ·  "
        "Taller de Comunicación para el Liderazgo Colaborativo",
    )
    c.setFont(FONT, 7.6)
    c.setFillColor(MUTED)
    c.drawString(
        title_x,
        h - 24.5 * mm,
        "Estudiante: Andres Barbudo Rodriguez  ·  Electricidad  ·  "
        "CFT Los Ríos, Sede Paillaco",
    )

    c.setFillColor(NAVY_DEEP)
    c.setFont(FONT_B, 8)
    c.drawRightString(w - 12 * mm, h - 12 * mm, page)
    c.setFillColor(MUTED)
    c.setFont(FONT, 7.4)
    c.drawRightString(
        w - 12 * mm,
        h - 18 * mm,
        f"Periodo  {fmt(PROJECT_START)}  —  {fmt(PROJECT_END)}",
    )
    cerradas = sum(1 for e in ETAPAS if e["pct"] >= 100)
    c.drawRightString(
        w - 12 * mm,
        h - 23.5 * mm,
        f"Fecha de estado  {fmt(STATUS)}   ·   {cerradas} de {len(ETAPAS)} etapas cerradas",
    )
    return h - header_h - 4 * mm


def draw_footer(c: canvas.Canvas, w: float) -> None:
    c.setFillColor(NAVY_DEEP)
    c.rect(0, 0, w, 9 * mm, fill=1, stroke=0)
    c.setFillColor(ORANGE)
    c.rect(0, 9 * mm, w, 1.3 * mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT, 6.8)
    c.drawString(
        12 * mm,
        3.5 * mm,
        "CFT Los Ríos  ·  Sede Paillaco  ·  Trabajo Práctico Aplicado  ·  "
        "esta carta no reemplaza el expediente técnico de la especialidad",
    )
    c.drawRightString(
        w - 12 * mm,
        3.5 * mm,
        "Hoy calcula y simula; no instala un filtro en la red",
    )


def draw_gantt_page(c: canvas.Canvas) -> None:
    w, h = landscape(A4)
    c.setFillColor(BG)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    top = draw_header(c, w, h, "01  /  02")
    draw_footer(c, w)

    left = 10 * mm
    right = w - 10 * mm
    y = top

    # Pitch
    pitch_h = 22 * mm
    c.setFillColor(white)
    c.roundRect(left, y - pitch_h, right - left, pitch_h, 2.2, fill=1, stroke=0)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    c.roundRect(left, y - pitch_h, right - left, pitch_h, 2.2, fill=0, stroke=1)
    c.setFillColor(ORANGE)
    c.rect(left, y - pitch_h, 2.2 * mm, pitch_h, fill=1, stroke=0)

    c.setFillColor(NAVY_DEEP)
    c.setFont(FONT_B, 7.4)
    c.drawString(left + 6 * mm, y - 5.2 * mm, "DE QUÉ TRATA ESTE PROYECTO")
    pitch = (
        "En tableros eléctricos que alimentan equipos de telecomunicaciones, ciertas corrientes "
        "no deseadas se suman en el cable neutro, lo calientan y acortan la vida de la instalación. "
        "Este trabajo no construye el filtro industrial: entrega una herramienta académica para "
        "calcular, simular y explicar ese problema, con pruebas seguras en el laboratorio del CFT. "
        "Esta carta muestra solo las etapas e hitos, en un lenguaje que permite coordinar el trabajo "
        "con la dupla docente y presentar el proyecto a un público no especialista."
    )
    c.setFillColor(INK)
    c.setFont(FONT, 7.6)
    for i, line in enumerate(wrap(c, pitch, FONT, 7.6, right - left - 14 * mm)):
        c.drawString(left + 6 * mm, y - 10.2 * mm - i * 3.5 * mm, line)

    y = y - pitch_h - 4 * mm
    label_w = 78 * mm
    chart_x = left + label_w
    chart_w = right - chart_x
    col_w = chart_w / N_WEEKS

    month_h = 6.2 * mm
    week_h = 7.2 * mm
    mile_h = 11 * mm
    footer_clear = 22 * mm
    n_rows = len(ETAPAS)
    usable = y - footer_clear - month_h - week_h - mile_h
    row_h = usable / n_rows
    grid_top = y
    grid_bottom = grid_top - month_h - week_h - n_rows * row_h

    c.setFillColor(NAVY_DEEP)
    c.rect(left, grid_top - month_h, label_w, month_h, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_B, 7.2)
    c.drawString(left + 3 * mm, grid_top - month_h + 1.9 * mm, "ETAPA")

    for name, a, b in MONTHS:
        x0 = week_x(chart_x, chart_w, a)
        x1 = week_x(chart_x, chart_w, b + 1)
        c.setFillColor(NAVY)
        c.rect(x0, grid_top - month_h, x1 - x0, month_h, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(FONT_B, 8)
        c.drawCentredString((x0 + x1) / 2, grid_top - month_h + 1.8 * mm, name)
        c.setStrokeColor(NAVY_DEEP)
        c.setLineWidth(0.35)
        c.line(x0, grid_top - month_h, x0, grid_bottom)

    c.setFillColor(HexColor("#EEF1F5"))
    c.rect(left, grid_top - month_h - week_h, label_w + chart_w, week_h, fill=1, stroke=0)
    today_week_idx = (STATUS - PROJECT_START).days // 7
    for i in range(N_WEEKS):
        x0 = chart_x + i * col_w
        d0 = week_start(i + 1)
        if i == today_week_idx:
            c.setFillColor(ORANGE)
            c.rect(x0, grid_top - month_h - week_h, col_w, week_h, fill=1, stroke=0)
        c.setFillColor(INK if i != today_week_idx else INK)
        c.setFont(FONT_B if i == today_week_idx else FONT, 6.2)
        c.drawCentredString(x0 + col_w / 2, grid_top - month_h - week_h + 3.8 * mm, f"S{i + 1:02d}")
        c.setFont(FONT, 5.6)
        c.setFillColor(INK if i == today_week_idx else MUTED)
        c.drawCentredString(x0 + col_w / 2, grid_top - month_h - week_h + 0.9 * mm, f"{d0.day:02d}")
        c.setStrokeColor(LINE)
        c.setLineWidth(0.25)
        c.line(x0, grid_top - month_h, x0, grid_bottom)

    for idx, row in enumerate(ETAPAS):
        y0 = grid_top - month_h - week_h - (idx + 1) * row_h
        c.setFillColor(white if idx % 2 == 0 else HexColor("#F7F9FC"))
        c.rect(left, y0, label_w + chart_w, row_h, fill=1, stroke=0)

        c.setFillColor(NAVY)
        c.setFont(FONT_B, 7.2)
        c.drawString(left + 2.4 * mm, y0 + row_h / 2 - 1.2 * mm, row["id"])
        c.setFillColor(INK)
        c.setFont(FONT, 8)
        c.drawString(left + 11 * mm, y0 + row_h / 2 - 1.2 * mm, row["name"])

        x0 = week_x(chart_x, chart_w, row["start"])
        x1 = week_x(chart_x, chart_w, row["finish"] + 1)
        pad = 3.2
        bar_y = y0 + pad
        bar_h = row_h - 2 * pad
        pct = row["pct"] / 100.0
        bw = x1 - x0 - 1.8
        bx = x0 + 0.9

        c.setFillColor(PLAN if pct < 1 else NAVY_DEEP)
        c.roundRect(bx, bar_y, bw, bar_h, 1.2, fill=1, stroke=0)
        if pct > 0:
            fill = NAVY_DEEP if pct >= 1 else ORANGE_DEEP
            c.setFillColor(fill)
            c.roundRect(bx, bar_y, max(2.0, bw * pct), bar_h, 1.2, fill=1, stroke=0)
        if pct >= 1 and bw > 22:
            c.setFillColor(white)
            c.setFont(FONT_B, 6.4)
            c.drawCentredString(bx + bw / 2, bar_y + bar_h / 2 - 1.8, "100 %")
        elif 0 < pct < 1 and bw > 28:
            c.setFillColor(INK)
            c.setFont(FONT_B, 6.4)
            c.drawCentredString(bx + bw / 2, bar_y + bar_h / 2 - 1.8, f"{row['pct']} %")

    today_week = 1 + (STATUS - PROJECT_START).days / 7
    tx = week_x(chart_x, chart_w, today_week)
    c.setStrokeColor(ORANGE_DEEP)
    c.setLineWidth(1.3)
    c.setDash(2, 1.6)
    c.line(tx, grid_bottom, tx, grid_top - month_h - week_h)
    c.setDash()

    c.setStrokeColor(NAVY_DEEP)
    c.setLineWidth(0.7)
    c.rect(left, grid_bottom, label_w + chart_w, grid_top - grid_bottom, fill=0, stroke=1)
    c.line(chart_x, grid_top, chart_x, grid_bottom)

    my = grid_bottom - mile_h - 1.6 * mm
    c.setFillColor(white)
    c.roundRect(left, my, label_w + chart_w, mile_h, 1.6, fill=1, stroke=0)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    c.roundRect(left, my, label_w + chart_w, mile_h, 1.6, fill=0, stroke=1)
    c.setFillColor(NAVY_DEEP)
    c.setFont(FONT_B, 7)
    c.drawString(left + 2.6 * mm, my + mile_h / 2 + 0.6 * mm, "HITOS")

    # Diamonds sit on the week of each hito. Labels that would collide
    # (H3 together with H4–H7 in late August) share one caption.
    xs_all = []
    for ms in HITOS:
        day_frac = (ms["date"] - week_start(ms["week"])).days / 7
        mx = week_x(chart_x, chart_w, ms["week"] + min(0.78, max(0.18, day_frac)))
        xs_all.append((ms, mx))
        passed = ms["date"] <= STATUS
        diamond(c, mx, my + mile_h / 2 + 2.0 * mm, 2.8, ORANGE if passed else INK)

    captions = [
        (["H1"], "H1"),
        (["H2"], "H2"),
        (["H3", "H4", "H5", "H6", "H7"], "H3–H7"),
        (["H8"], "H8"),
    ]
    lookup = {ms["id"]: mx for ms, mx in xs_all}
    for ids, label in captions:
        points = [lookup[i] for i in ids if i in lookup]
        if not points:
            continue
        cx = sum(points) / len(points)
        last = next(ms for ms in HITOS if ms["id"] == ids[-1])
        c.setFillColor(INK if last["date"] <= STATUS else MUTED)
        c.setFont(FONT_B, 6)
        c.drawCentredString(cx, my + 1.3 * mm, label)

    ly = 12.2 * mm
    c.setFont(FONT, 7)
    items = [
        (NAVY_DEEP, "Etapa terminada"),
        (ORANGE_DEEP, "Etapa en curso"),
        (PLAN, "Etapa planificada"),
        (ORANGE, "Hito cumplido"),
        (INK, "Hito pendiente"),
    ]
    x = left
    for color, label in items:
        if "Hito" in label:
            diamond(c, x + 2.4 * mm, ly + 1.5 * mm, 2.5, color)
            c.setFillColor(GRAPHITE)
            c.drawString(x + 8 * mm, ly + 0.3 * mm, label)
            x += 42 * mm
        else:
            c.setFillColor(color)
            c.roundRect(x, ly, 7 * mm, 2.8 * mm, 0.8, fill=1, stroke=0)
            c.setFillColor(GRAPHITE)
            c.drawString(x + 9 * mm, ly + 0.3 * mm, label)
            x += 42 * mm
    c.setStrokeColor(ORANGE_DEEP)
    c.setLineWidth(1.3)
    c.setDash(2, 1.6)
    c.line(x, ly + 1.4 * mm, x + 8 * mm, ly + 1.4 * mm)
    c.setDash()
    c.setFillColor(GRAPHITE)
    c.drawString(x + 10 * mm, ly + 0.3 * mm, "Hoy (28-ago)")

    c.showPage()


def card_header(c: canvas.Canvas, x: float, y: float, cw: float, title: str) -> None:
    c.setFillColor(NAVY_DEEP)
    c.rect(x, y - 7.2 * mm, cw, 7.2 * mm, fill=1, stroke=0)
    c.setFillColor(ORANGE)
    c.rect(x, y - 7.2 * mm, 2.2 * mm, 7.2 * mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_B, 8.2)
    c.drawString(x + 6 * mm, y - 4.9 * mm, title)


def draw_notes_page(c: canvas.Canvas) -> None:
    w, h = landscape(A4)
    c.setFillColor(BG)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    top = draw_header(c, w, h, "02  /  02")
    draw_footer(c, w)

    left = 10 * mm
    right = w - 10 * mm
    y = top - 1 * mm

    c.setFillColor(white)
    table_h = 80 * mm
    c.roundRect(left, y - table_h, right - left, table_h, 2.2, fill=1, stroke=0)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    c.roundRect(left, y - table_h, right - left, table_h, 2.2, fill=0, stroke=1)
    card_header(c, left, y, right - left, "LOS OCHO HITOS, EN LENGUAJE DE ESTA ASIGNATURA")

    cols = [
        ("ID", 12 * mm),
        ("Hito", 58 * mm),
        ("Fecha", 28 * mm),
        ("Estado", 22 * mm),
        ("Qué significa", 92 * mm),
        ("Cómo se comunica", 65 * mm),
    ]
    table_w = sum(cw for _, cw in cols)
    extra = (right - left) - table_w
    cols[4] = (cols[4][0], cols[4][1] + extra * 0.6)
    cols[5] = (cols[5][0], cols[5][1] + extra * 0.4)
    table_w = sum(cw for _, cw in cols)

    hy = y - 7.2 * mm
    header_h = 6.4 * mm
    c.setFillColor(HexColor("#EEF1F5"))
    c.rect(left, hy - header_h, table_w, header_h, fill=1, stroke=0)
    c.setFillColor(NAVY_DEEP)
    c.setFont(FONT_B, 6.6)
    x = left
    for title, cw in cols:
        c.drawString(x + 1.8 * mm, hy - header_h + 2.2 * mm, title.upper())
        x += cw
    hy -= header_h

    row_h = (table_h - 7.2 * mm - header_h) / len(HITOS)
    for i, ms in enumerate(HITOS):
        c.setFillColor(white if i % 2 == 0 else HexColor("#F7F9FC"))
        c.rect(left, hy - row_h, table_w, row_h, fill=1, stroke=0)
        st = "Cumplido" if ms["date"] <= STATUS else "Pendiente"
        vals = [
            ms["id"],
            ms["name"],
            fmt(ms["date"]),
            st,
            ms["significado"],
            ms["comunica"],
        ]
        x = left
        for (title, cw), val in zip(cols, vals):
            if title == "ID":
                c.setFillColor(NAVY)
                c.setFont(FONT_B, 7)
            elif title == "Estado":
                c.setFillColor(OK if st == "Cumplido" else MUTED)
                c.setFont(FONT_B, 7)
            elif title == "Hito":
                c.setFillColor(INK)
                c.setFont(FONT_B, 7)
            else:
                c.setFillColor(INK)
                c.setFont(FONT, 6.8)
            text_y = hy - row_h / 2 - 1.1 * mm
            if title in ("Qué significa",) and c.stringWidth(val, FONT, 6.8) > cw - 4 * mm:
                lines = wrap(c, val, FONT, 6.8, cw - 4 * mm)
                text_y = hy - 3.2 * mm
                for j, line in enumerate(lines[:2]):
                    c.drawString(x + 1.8 * mm, text_y - j * 3.1 * mm, line)
            else:
                c.drawString(x + 1.8 * mm, text_y, val)
            x += cw
        hy -= row_h

    y = y - table_h - 4 * mm
    gap = 4.5 * mm
    col_w = (right - left - 2 * gap) / 3
    card_h = 48 * mm
    next_h = 16.5 * mm

    def body_card(x, title, lines_fn):
        c.setFillColor(white)
        c.roundRect(x, y - card_h, col_w, card_h, 2.2, fill=1, stroke=0)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.4)
        c.roundRect(x, y - card_h, col_w, card_h, 2.2, fill=0, stroke=1)
        card_header(c, x, y, col_w, title)
        lines_fn(x, y - 12 * mm)

    def para_quien(x, yy):
        bloques = [
            (
                "Con esta asignatura",
                "Etapas, hitos y acuerdos. Esta carta.",
            ),
            (
                "Con la especialidad",
                "El expediente técnico (cálculos, pruebas y archivos).",
            ),
            (
                "En el informe escrito",
                "Redacción formal de la memoria del proyecto.",
            ),
            (
                "En la defensa oral",
                "Oratoria, demostración en pantalla y respuesta a preguntas.",
            ),
        ]
        ty = yy
        for title, body in bloques:
            c.setFillColor(ORANGE)
            c.circle(x + 7 * mm, ty + 1.1 * mm, 1.15 * mm, fill=1, stroke=0)
            c.setFillColor(NAVY_DEEP)
            c.setFont(FONT_B, 7.2)
            c.drawString(x + 11 * mm, ty, title)
            c.setFillColor(INK)
            c.setFont(FONT, 7)
            for j, line in enumerate(wrap(c, body, FONT, 7, col_w - 16 * mm)):
                c.drawString(x + 11 * mm, ty - 3.6 * mm - j * 3.2 * mm, line)
            ty -= 8.8 * mm

    def cadena(x, yy):
        c.setFillColor(INK)
        c.setFont(FONT, 7.4)
        text = (
            "La ruta del proyecto, leída como un proceso de comunicación, es esta cadena:"
        )
        ty = yy
        for i, line in enumerate(wrap(c, text, FONT, 7.4, col_w - 12 * mm)):
            c.drawString(x + 6 * mm, ty - i * 3.4 * mm, line)
        steps = [
            "1. Diagnosticar el problema",
            "2. Calcular el tablero",
            "3. Estudiar las corrientes no deseadas",
            "4. Preparar la demostración",
            "5. Reunir evidencias",
            "6. Escribir el informe",
            "7. Defenderlo en voz alta",
        ]
        ty -= 8.2 * mm
        for step in steps:
            c.setFillColor(NAVY)
            c.roundRect(x + 6 * mm, ty - 1.4 * mm, 2.2 * mm, 2.2 * mm, 0.4, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont(FONT, 7.2)
            c.drawString(x + 11 * mm, ty - 0.6 * mm, step)
            ty -= 4.35 * mm

    def fuera(x, yy):
        items = [
            "No se instala un filtro en la red eléctrica.",
            "No se trabaja con 400 V ni con corrientes de centenares de amperes.",
            "No es un producto en venta ni un certificado de norma.",
            "Lo que se defiende es el cálculo, la simulación y la explicación del problema.",
            "El autor es uno. Se coordina con la dupla docente, el profesor guía y el pañol del CFT.",
        ]
        ty = yy + 1 * mm
        for item in items:
            c.setFillColor(ORANGE_DEEP)
            c.circle(x + 7.2 * mm, ty + 1.0 * mm, 1.15 * mm, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont(FONT, 7.2)
            lines = wrap(c, item, FONT, 7.2, col_w - 16 * mm)
            for j, line in enumerate(lines):
                c.drawString(x + 11 * mm, ty - j * 3.3 * mm, line)
            ty -= max(1, len(lines)) * 3.3 * mm + 1.6 * mm

    body_card(left, "A QUIÉN SE HABLA Y CÓMO", para_quien)
    body_card(left + col_w + gap, "CADENA DEL PROYECTO", cadena)
    body_card(left + 2 * (col_w + gap), "LÍMITES Y COORDINACIÓN", fuera)

    ny = y - card_h - 4 * mm
    c.setFillColor(white)
    c.roundRect(left, ny - next_h, right - left, next_h, 2.2, fill=1, stroke=0)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    c.roundRect(left, ny - next_h, right - left, next_h, 2.2, fill=0, stroke=1)
    card_header(c, left, ny, right - left, "QUÉ VIENE AHORA  ·  DESDE EL 28 DE AGOSTO")
    proximos = [
        ("1", "Recoger la retroalimentación del profesor guía y corregir el informe."),
        ("2", "Ensayar la demostración oral, con un lenguaje claro para la comisión."),
        ("3", "Defensa oral del proyecto: 4 de diciembre de 2026."),
    ]
    pw = (right - left) / 3
    for i, (num, text) in enumerate(proximos):
        px = left + 6 * mm + i * pw
        c.setFillColor(ORANGE)
        c.circle(px + 2.2 * mm, ny - 12.6 * mm, 2.3 * mm, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(FONT_B, 7)
        c.drawCentredString(px + 2.2 * mm, ny - 13.5 * mm, num)
        c.setFillColor(INK)
        c.setFont(FONT, 7.3)
        for j, line in enumerate(wrap(c, text, FONT, 7.3, pw - 16 * mm)):
            c.drawString(px + 7 * mm, ny - 13.2 * mm - j * 3.3 * mm, line)

    c.showPage()


def main() -> None:
    c = canvas.Canvas(str(PDF_PATH), pagesize=landscape(A4))
    c.setTitle("Carta Gantt TPA — versión de comunicación")
    c.setAuthor("Andres Barbudo Rodriguez")
    c.setSubject(
        "Etapas e hitos del Trabajo Práctico Aplicado, "
        "redactados para el Taller de Comunicación para el Liderazgo Colaborativo"
    )
    c.setKeywords("TPA, carta Gantt, comunicación, CFT Los Ríos, Paillaco")
    draw_gantt_page(c)
    draw_notes_page(c)
    c.save()
    if CLASS_COPY.parent.exists():
        CLASS_COPY.write_bytes(PDF_PATH.read_bytes())
        print(f"COPIA  {CLASS_COPY}")
    print(f"PDF    {PDF_PATH}")
    print(f"Avance {global_progress()} %")


if __name__ == "__main__":
    main()
