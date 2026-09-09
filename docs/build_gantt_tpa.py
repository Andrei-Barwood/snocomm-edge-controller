#!/usr/bin/env python3
"""Carta Gantt del TPA — AHF Edge Controller (Snocomm)."""

from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

OUT_DIR = Path(__file__).resolve().parent
PDF_PATH = OUT_DIR / "CARTA_GANTT_TPA.pdf"
CSV_PATH = OUT_DIR / "CARTA_GANTT_TPA.csv"
MD_PATH = OUT_DIR / "CARTA_GANTT_TPA.md"

INK = HexColor("#303030")
GRAPHITE = HexColor("#4F4F4F")
PAPER = HexColor("#D7E0EC")
GOLD = HexColor("#E3CA75")
GOLD_DEEP = HexColor("#CCB244")
INDIGO = HexColor("#5A64BF")
INDIGO_DEEP = HexColor("#485199")
MUTED = HexColor("#626975")
LINE = HexColor("#BCC7D6")
DANGER = HexColor("#8F3232")
BG = HexColor("#F5F7FA")
PLAN = HexColor("#C5CED9")
OK = HexColor("#3D7A5A")

PROJECT_START = date(2026, 6, 8)  # lunes semana 1
STATUS = date(2026, 8, 23)
N_WEEKS = 26
PROJECT_END = PROJECT_START + timedelta(weeks=N_WEEKS) - timedelta(days=1)

# Ritmo medido el 21-ago-2026 (no es el ritmo semanal):
# 6 de 16 prompts (P02–P07) en 2,5 h sin pausa · 3 % Super Grok.
# Plan restante: 2 sesiones/semana, 1–2 prompts/sesión. Cuota no es el cuello.

# kind: summary | task | milestone
# start/finish are 1-based inclusive week numbers
ROWS = [
    {"id": "F0", "name": "F0  Gestión del TPA", "start": 1, "finish": 26, "pct": 86, "kind": "summary", "pred": "—"},
    {"id": "0.1", "name": "Kickoff, problema y alcance académico", "start": 1, "finish": 2, "pct": 100, "kind": "task", "pred": "—"},
    {"id": "0.2", "name": "Revisión normativa IEC 61439 / RIC / IEC 62477", "start": 1, "finish": 4, "pct": 100, "kind": "task", "pred": "0.1"},
    {"id": "0.3", "name": "EDT, riesgos y carta Gantt (documento vivo)", "start": 2, "finish": 11, "pct": 100, "kind": "task", "pred": "0.1"},
    {"id": "F1", "name": "F1  Arquitectura de software de borde", "start": 2, "finish": 6, "pct": 100, "kind": "summary", "pred": "0.1"},
    {"id": "1.1", "name": "Tres procesos IPC, config y supervisory", "start": 2, "finish": 4, "pct": 100, "kind": "task", "pred": "0.1"},
    {"id": "1.2", "name": "Docker, abstracción ADC y memoria compartida", "start": 3, "finish": 6, "pct": 100, "kind": "task", "pred": "1.1"},
    {"id": "F2", "name": "F2  Preingeniería TAN (IEC 61439)", "start": 3, "finish": 8, "pct": 100, "kind": "summary", "pred": "0.2"},
    {"id": "2.1", "name": "Cálculos I, Icw/Icc, calentamiento y forma", "start": 3, "finish": 5, "pct": 100, "kind": "task", "pred": "0.2"},
    {"id": "2.2", "name": "CLI, catálogo XL3 y expediente Excel/PDF", "start": 5, "finish": 7, "pct": 100, "kind": "task", "pred": "2.1"},
    {"id": "2.3", "name": "Pruebas de cálculos y reglas TAN", "start": 6, "finish": 8, "pct": 100, "kind": "task", "pred": "2.2"},
    {"id": "F3", "name": "F3  DSP 3P+N sobre señales patrón", "start": 5, "finish": 10, "pct": 100, "kind": "summary", "pred": "1.1"},
    {"id": "3.1", "name": "Generador de señales patrón 50 Hz 3P+N", "start": 5, "finish": 7, "pct": 100, "kind": "task", "pred": "1.1"},
    {"id": "3.2", "name": "Clarke ab0, SRF-PLL y extracción H3/H5/H7", "start": 6, "finish": 9, "pct": 100, "kind": "task", "pred": "3.1"},
    {"id": "3.3", "name": "Pruebas DSP y THDi académico Ih/I1", "start": 8, "finish": 10, "pct": 100, "kind": "task", "pred": "3.2"},
    {"id": "F4", "name": "F4  Operador, SCADA y proyecto común", "start": 7, "finish": 11, "pct": 100, "kind": "summary", "pred": "3.2"},
    {"id": "4.1", "name": "Dashboard Monitor AHF y telemetría", "start": 7, "finish": 10, "pct": 100, "kind": "task", "pred": "3.2"},
    {"id": "4.2", "name": "Vista TAN e importación CSV/JSON de campaña", "start": 9, "finish": 11, "pct": 100, "kind": "task", "pred": "2.2; 4.1"},
    {"id": "4.3", "name": "Modbus TLS, InfluxDB y proyecto THDi-TAN", "start": 8, "finish": 11, "pct": 100, "kind": "task", "pred": "4.1"},
    {"id": "F5", "name": "F5  SIL / HIL banco 24 V", "start": 10, "finish": 11, "pct": 100, "kind": "summary", "pred": "4.1"},
    {"id": "5.1", "name": "Máquina de estados, E-stop e interlocks", "start": 10, "finish": 11, "pct": 100, "kind": "task", "pred": "4.1"},
    {"id": "5.2", "name": "Vista Banco 24 V y paquete documental pañol", "start": 11, "finish": 11, "pct": 100, "kind": "task", "pred": "5.1"},
    {"id": "5.3", "name": "Criterios SIL y pruebas de potencia simulada", "start": 11, "finish": 11, "pct": 100, "kind": "task", "pred": "5.1"},
    {"id": "F6", "name": "F6  Validación y evidencias TPA", "start": 11, "finish": 18, "pct": 51, "kind": "summary", "pred": "5.3"},
    {"id": "6.1", "name": "Suite de regresión y casos de demostración", "start": 11, "finish": 12, "pct": 100, "kind": "task", "pred": "2.3; 3.3; 5.3"},
    {"id": "6.2", "name": "Informe de evidencias y límites declarados", "start": 12, "finish": 12, "pct": 100, "kind": "task", "pred": "6.1"},
    {"id": "6.3", "name": "Campaña pañol 24 V (KPS305D + GA1102CAL)", "start": 12, "finish": 18, "pct": 30, "kind": "task", "pred": "5.2"},
    {"id": "F7", "name": "F7  Memoria técnica y defensa", "start": 13, "finish": 26, "pct": 47, "kind": "summary", "pred": "6.2"},
    {"id": "7.1", "name": "Borrador de memoria técnica (P09–P12)", "start": 13, "finish": 16, "pct": 100, "kind": "task", "pred": "6.2"},
    {"id": "7.3", "name": "Presentación PPTX y banco de preguntas", "start": 16, "finish": 17, "pct": 100, "kind": "task", "pred": "7.1"},
    {"id": "7.2", "name": "Revisión del profesor guía y correcciones", "start": 17, "finish": 21, "pct": 0, "kind": "task", "pred": "7.1"},
    {"id": "7.5", "name": "Guion y ensayo demo live (P16)", "start": 22, "finish": 24, "pct": 50, "kind": "task", "pred": "6.2; 7.3"},
    {"id": "7.4", "name": "Entrega final y defensa del TPA", "start": 25, "finish": 26, "pct": 0, "kind": "task", "pred": "7.2; 7.3; 7.5"},
]

MILESTONES = [
    {"id": "M1", "name": "Alcance TPA congelado", "week": 2, "date": date(2026, 6, 21)},
    {"id": "M2", "name": "TAN-Telecom operable", "week": 7, "date": date(2026, 7, 26)},
    {"id": "M3", "name": "DSP validado con patrones", "week": 10, "date": date(2026, 8, 16)},
    {"id": "M4", "name": "Plataforma de 3 vistas integrada", "week": 11, "date": date(2026, 8, 21)},
    {"id": "M5", "name": "HIL SIL cerrado (sin salidas físicas)", "week": 11, "date": date(2026, 8, 21)},
    {"id": "M6", "name": "Paquete de evidencias TPA", "week": 11, "date": date(2026, 8, 23)},
    {"id": "M7", "name": "Borrador de memoria", "week": 11, "date": date(2026, 8, 23)},
    {"id": "M8", "name": "Defensa del TPA", "week": 26, "date": date(2026, 12, 4)},
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


def status_of(pct: int, finish: int) -> str:
    if pct >= 100:
        return "Completada"
    today_week = ((STATUS - PROJECT_START).days // 7) + 1
    if pct > 0:
        return "En curso"
    if finish < today_week:
        return "Atrasada"
    return "Planificada"


def global_progress() -> int:
    tasks = [r for r in ROWS if r["kind"] == "task"]
    num = sum((r["finish"] - r["start"] + 1) * r["pct"] for r in tasks)
    den = sum(r["finish"] - r["start"] + 1 for r in tasks)
    return round(num / den)


def register_fonts() -> tuple[str, str]:
    candidates = [
        ("/System/Library/Fonts/Supplemental/Arial.ttf",
         "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        ("/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    for regular, bold in candidates:
        if Path(regular).exists() and Path(bold).exists():
            pdfmetrics.registerFont(TTFont("Body", regular))
            pdfmetrics.registerFont(TTFont("Body-Bold", bold))
            return "Body", "Body-Bold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_B = register_fonts()


def draw_header(c: canvas.Canvas, w: float, h: float, page: str) -> float:
    c.setFillColor(INK)
    c.rect(0, h - 28 * mm, w, 28 * mm, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, h - 28 * mm, w, 2.2 * mm, fill=1, stroke=0)

    c.setFillColor(GOLD)
    c.setFont(FONT_B, 11)
    c.drawString(14 * mm, h - 9 * mm, "SNOCOMM")
    c.setFillColor(PAPER)
    c.setFont(FONT, 8)
    c.drawString(38 * mm, h - 9 * mm, "ENERGY CONTROL")

    c.setFillColor(white)
    c.setFont(FONT_B, 14)
    c.drawString(14 * mm, h - 16.5 * mm, "Carta Gantt  ·  Trabajo Práctico Aplicado")
    c.setFont(FONT, 8.5)
    c.setFillColor(PAPER)
    c.drawString(
        14 * mm,
        h - 22.5 * mm,
        "Controlador de borde para filtro activo de armónicos (AHF)  ·  "
        "Preingeniería BT · DSP 3P+N sobre señales patrón · validación SIL 24 V",
    )

    c.setFillColor(GOLD)
    c.setFont(FONT_B, 8)
    c.drawRightString(w - 14 * mm, h - 9 * mm, page)
    c.setFillColor(PAPER)
    c.setFont(FONT, 7.5)
    c.drawRightString(w - 14 * mm, h - 16 * mm, f"Periodo  {fmt(PROJECT_START)}  —  {fmt(PROJECT_END)}")
    c.drawRightString(w - 14 * mm, h - 21.5 * mm, f"Fecha de estado  {fmt(STATUS)}   ·   Avance ponderado  {global_progress()} %")
    return h - 32 * mm


def draw_footer(c: canvas.Canvas, w: float) -> None:
    c.setFillColor(INK)
    c.rect(0, 0, w, 10 * mm, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, 10 * mm, w, 1.4 * mm, fill=1, stroke=0)
    c.setFillColor(PAPER)
    c.setFont(FONT, 7)
    c.drawString(14 * mm, 4 * mm, "Repositorio snocomm-edge-controller  ·  licencia MIT  ·  uso académico TPA, no es producto 400 V")
    c.drawRightString(w - 14 * mm, 4 * mm, "Hoy calcula y simula; no mide con instrumento certificado ni inyecta corriente")


def week_x(chart_x: float, chart_w: float, week: float) -> float:
    return chart_x + (week - 1) * (chart_w / N_WEEKS)


def diamond(c: canvas.Canvas, x: float, y: float, s: float, fill: Color, stroke: Color | None = None) -> None:
    p = c.beginPath()
    p.moveTo(x, y + s)
    p.lineTo(x + s, y)
    p.lineTo(x, y - s)
    p.lineTo(x - s, y)
    p.close()
    c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(0.6)
        c.drawPath(p, fill=1, stroke=1)
    else:
        c.drawPath(p, fill=1, stroke=0)


def draw_gantt_page(c: canvas.Canvas) -> None:
    w, h = landscape(A3)
    c.setFillColor(BG)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    top = draw_header(c, w, h, "01  /  CARTA GANTT")
    draw_footer(c, w)

    left = 12 * mm
    right = w - 12 * mm
    label_w = 92 * mm
    chart_x = left + label_w
    chart_w = right - chart_x
    col_w = chart_w / N_WEEKS

    # meta strip
    y = top
    c.setFillColor(white)
    c.roundRect(left, y - 16 * mm, right - left, 14 * mm, 2, fill=1, stroke=0)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    c.roundRect(left, y - 16 * mm, right - left, 14 * mm, 2, fill=0, stroke=1)

    metas = [
        ("Autor", "Andres Barbudo Rodriguez"),
        ("Carrera / tipo", "Electricidad  ·  TPA CFT Paillaco"),
        ("Unidad de tiempo", "Semana calendario (lunes a domingo)"),
        ("Alcance TPA", "Cálculo + SIL 24 V pañol. Sin 400 V / 500 kW."),
    ]
    mw = (right - left) / 4
    for i, (k, v) in enumerate(metas):
        mx = left + 4 * mm + i * mw
        c.setFillColor(INDIGO_DEEP)
        c.setFont(FONT_B, 6.5)
        c.drawString(mx, y - 6 * mm, k.upper())
        c.setFillColor(INK)
        c.setFont(FONT, 7.2)
        c.drawString(mx, y - 11.5 * mm, v)

    grid_top = y - 20 * mm
    month_h = 6.5 * mm
    week_h = 6 * mm
    footer_clear = 28 * mm
    mile_h = 9 * mm
    n_rows = len(ROWS)
    usable = grid_top - footer_clear - month_h - week_h - mile_h
    row_h = usable / n_rows
    grid_bottom = grid_top - month_h - week_h - n_rows * row_h

    # month + week headers
    c.setFillColor(INK)
    c.rect(left, grid_top - month_h, label_w, month_h, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(FONT_B, 7)
    c.drawString(left + 3 * mm, grid_top - month_h + 2 * mm, "EDT  /  ACTIVIDAD")

    for name, a, b in MONTHS:
        x0 = week_x(chart_x, chart_w, a)
        x1 = week_x(chart_x, chart_w, b + 1)
        c.setFillColor(GRAPHITE)
        c.rect(x0, grid_top - month_h, x1 - x0, month_h, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont(FONT_B, 8)
        c.drawCentredString((x0 + x1) / 2, grid_top - month_h + 2 * mm, name)
        c.setStrokeColor(INK)
        c.setLineWidth(0.4)
        c.line(x0, grid_top - month_h, x0, grid_bottom)

    c.setFillColor(HexColor("#ECEFF4"))
    c.rect(left, grid_top - month_h - week_h, label_w + chart_w, week_h, fill=1, stroke=0)
    today_week_idx = (STATUS - PROJECT_START).days // 7  # 0-based
    c.setFont(FONT, 6)
    for i in range(N_WEEKS):
        x0 = chart_x + i * col_w
        d0 = week_start(i + 1)
        if i == today_week_idx:
            c.setFillColor(GOLD)
            c.rect(x0, grid_top - month_h - week_h, col_w, week_h, fill=1, stroke=0)
        c.setFillColor(INK if i % 2 == 0 else GRAPHITE)
        if i == today_week_idx:
            c.setFillColor(INK)
            c.setFont(FONT_B, 6)
        c.drawCentredString(x0 + col_w / 2, grid_top - month_h - week_h + 3.4 * mm, f"S{i + 1:02d}")
        c.setFont(FONT, 5.5)
        c.setFillColor(INK if i == today_week_idx else MUTED)
        c.drawCentredString(x0 + col_w / 2, grid_top - month_h - week_h + 0.8 * mm, f"{d0.day:02d}")
        c.setStrokeColor(LINE)
        c.setLineWidth(0.25)
        c.line(x0, grid_top - month_h, x0, grid_bottom)

    # rows
    for idx, row in enumerate(ROWS):
        y0 = grid_top - month_h - week_h - (idx + 1) * row_h
        is_sum = row["kind"] == "summary"
        if is_sum:
            c.setFillColor(HexColor("#E8EBF2"))
        elif idx % 2 == 0:
            c.setFillColor(white)
        else:
            c.setFillColor(HexColor("#F7F9FC"))
        c.rect(left, y0, label_w + chart_w, row_h, fill=1, stroke=0)

        c.setFillColor(INDIGO_DEEP if is_sum else MUTED)
        c.setFont(FONT_B, 6.4 if is_sum else 6)
        c.drawString(left + 2.2 * mm, y0 + row_h / 2 - 1.1 * mm, row["id"])
        c.setFillColor(INK)
        c.setFont(FONT_B if is_sum else FONT, 7 if is_sum else 6.6)
        name = row["name"]
        if name.startswith("F") and "  " in name:
            name = name.split("  ", 1)[1]
        c.drawString(left + 12 * mm, y0 + row_h / 2 - 1.1 * mm, name)

        x0 = week_x(chart_x, chart_w, row["start"])
        x1 = week_x(chart_x, chart_w, row["finish"] + 1)
        pad = 1.6 if is_sum else 2.3
        bar_y = y0 + pad
        bar_h = row_h - 2 * pad
        pct = row["pct"] / 100.0

        bw = x1 - x0 - 1.6
        bx = x0 + 0.8
        if is_sum:
            c.setFillColor(INK)
            c.rect(bx, bar_y + bar_h * 0.28, bw, bar_h * 0.44, fill=1, stroke=0)
            if pct > 0:
                fill = INDIGO if pct >= 1 else GOLD
                c.setFillColor(fill)
                c.rect(bx, bar_y + bar_h * 0.28, bw * pct, bar_h * 0.44, fill=1, stroke=0)
            c.setFillColor(INK)
            c.rect(x0 + 0.4, bar_y + 0.4, 1.6, bar_h - 0.8, fill=1, stroke=0)
            c.rect(x1 - 2.0, bar_y + 0.4, 1.6, bar_h - 0.8, fill=1, stroke=0)
        else:
            c.setFillColor(PLAN if pct < 1 else INDIGO_DEEP)
            c.rect(bx, bar_y, bw, bar_h, fill=1, stroke=0)
            if pct > 0:
                fill = INDIGO_DEEP if pct >= 1 else GOLD_DEEP
                c.setFillColor(fill)
                c.rect(bx, bar_y, max(1.2, bw * pct), bar_h, fill=1, stroke=0)
            if pct >= 1 and bw > 18:
                c.setFillColor(white)
                c.setFont(FONT_B, 5.5)
                c.drawCentredString(bx + bw / 2, bar_y + bar_h / 2 - 1.5, "100%")
            elif 0 < pct < 1 and bw > 22:
                c.setFillColor(INK)
                c.setFont(FONT_B, 5.5)
                c.drawCentredString(bx + bw / 2, bar_y + bar_h / 2 - 1.5, f"{row['pct']}%")

    # today line through the chart body
    today_week = 1 + (STATUS - PROJECT_START).days / 7
    tx = week_x(chart_x, chart_w, today_week)
    c.setStrokeColor(GOLD_DEEP)
    c.setLineWidth(1.35)
    c.setDash(2, 1.5)
    c.line(tx, grid_bottom, tx, grid_top - month_h - week_h)
    c.setDash()

    # outer frame
    c.setStrokeColor(INK)
    c.setLineWidth(0.7)
    c.rect(left, grid_bottom, label_w + chart_w, grid_top - grid_bottom, fill=0, stroke=1)
    c.line(chart_x, grid_top, chart_x, grid_bottom)

    # milestones strip (above legend)
    my = grid_bottom - mile_h - 1.5 * mm
    c.setFillColor(white)
    c.roundRect(left, my, label_w + chart_w, mile_h, 1.5, fill=1, stroke=0)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    c.roundRect(left, my, label_w + chart_w, mile_h, 1.5, fill=0, stroke=1)
    c.setFillColor(INDIGO_DEEP)
    c.setFont(FONT_B, 6.5)
    c.drawString(left + 2.4 * mm, my + mile_h / 2 - 1.1 * mm, "HITOS")
    seen_week: dict[int, int] = {}
    for ms in MILESTONES:
        slot = seen_week.get(ms["week"], 0)
        seen_week[ms["week"]] = slot + 1
        mx = week_x(chart_x, chart_w, ms["week"] + 0.32 + slot * 0.36)
        passed = ms["date"] <= STATUS
        diamond(c, mx, my + mile_h / 2 + 0.8 * mm, 3.0, GOLD if passed else INK, INK)
        c.setFillColor(INK if passed else MUTED)
        c.setFont(FONT_B, 5.6)
        c.drawCentredString(mx, my + 1.1 * mm, ms["id"])

    # legend under hitos, above footer
    ly = 13.2 * mm
    c.setFont(FONT, 6.6)
    items = [
        (INK, "Fase (resumen)"),
        (INDIGO_DEEP, "Actividad completada"),
        (GOLD_DEEP, "Actividad en curso"),
        (PLAN, "Actividad planificada"),
        (GOLD, "Hito cumplido"),
        (INK, "Hito pendiente"),
    ]
    x = left
    for color, label in items:
        c.setFillColor(color)
        if "Hito" in label:
            diamond(c, x + 2.2 * mm, ly + 1.4 * mm, 2.4, color, INK)
        else:
            c.rect(x, ly, 7 * mm, 2.6 * mm, fill=1, stroke=0)
        c.setFillColor(GRAPHITE)
        c.drawString(x + 9 * mm, ly + 0.4 * mm, label)
        x += 46 * mm
    c.setStrokeColor(GOLD_DEEP)
    c.setLineWidth(1.3)
    c.setDash(2, 1.5)
    c.line(x, ly + 1.3 * mm, x + 8 * mm, ly + 1.3 * mm)
    c.setDash()
    c.setFillColor(GRAPHITE)
    c.drawString(x + 10 * mm, ly + 0.4 * mm, "Fecha de estado")

    c.showPage()


def draw_table_page(c: canvas.Canvas) -> None:
    w, h = landscape(A3)
    c.setFillColor(BG)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    top = draw_header(c, w, h, "02  /  EDT Y PROGRAMACIÓN")
    draw_footer(c, w)

    left = 12 * mm
    right = w - 12 * mm
    y = top - 2 * mm

    c.setFillColor(INK)
    c.setFont(FONT_B, 11)
    c.drawString(left, y - 5 * mm, "Estructura de desglose del trabajo (EDT) y calendario")
    c.setFillColor(MUTED)
    c.setFont(FONT, 8)
    c.drawString(left, y - 10 * mm, "Duraciones en semanas calendario. Predecesoras según dependencias técnicas del repositorio, no según software de project.")
    y -= 14 * mm

    cols = [
        ("ID", 16 * mm),
        ("Actividad", 92 * mm),
        ("Inicio", 24 * mm),
        ("Término", 24 * mm),
        ("Sem.", 12 * mm),
        ("Predecesoras", 38 * mm),
        ("Avance", 16 * mm),
        ("Estado", 26 * mm),
        ("Entregable en el repo", 78 * mm),
    ]
    deliverable = {
        "F0": "docs/, README, alcance TPA",
        "0.1": "README: alcance académico y prohibiciones",
        "0.2": "docs/PRODUCT_ROADMAP_CHILE.md",
        "0.3": "docs/CARTA_GANTT_TPA.pdf (este documento)",
        "F1": "main_industrial.py, docker-compose.yml",
        "1.1": "hard_realtime_loop.py, supervisory_process.py",
        "1.2": "adc_hardware_driver.py, Dockerfile",
        "F2": "paquete tan_telecom/",
        "2.1": "tan_telecom/calculations.py, rules.py",
        "2.2": "CLI, export Excel/PDF, catálogo xl3",
        "2.3": "tan_telecom/tests/",
        "F3": "dsp/core.py, dsp/patterns.py",
        "3.1": "signal_generator.py, dsp/patterns.py",
        "3.2": "dsp/core.py (Clarke, PLL, H3/H5/H7)",
        "3.3": "tests/test_dsp.py",
        "F4": "templates/, static/, web_visualizer.py",
        "4.1": "Monitor AHF (index.html + app.js)",
        "4.2": "acquisition/, procedimiento scope 24 V",
        "4.3": "project_store.py (Modbus/Influx = capacidad, no defensa)",
        "F5": "power_stage/, hil_app.py, matriz SIL",
        "5.1": "power_stage/controller.py",
        "5.2": "BANCO_FISICO_24V.md, inventario, bench_package.py",
        "5.3": "MATRIZ_SIL_TPA.md, tests/test_power_stage.py",
        "F6": "tests/, output/tpa/",
        "6.1": "test_tpa_smoke + output/tpa/ (P08: casos demo)",
        "6.2": "docs/INFORME_EVIDENCIAS_TPA.md (P08)",
        "6.3": "CSV real Gratten; procedimiento P06 ya existe (PLUS)",
        "F7": "docs/memoria/ y lámina de defensa",
        "7.1": "docs/memoria/ capítulos 1–7 (P09–P12)",
        "7.2": "Versión corregida según guía (hasta 31-oct)",
        "7.3": "DEFENSA_TPA.pptx y PREGUNTAS_DEFENSA.md",
        "7.5": "docs/DEMO_LIVE_EXAMEN.md (pañol o aula)",
        "7.4": "Acta de defensa / entrega final",
    }

    table_w = sum(w_ for _, w_ in cols)
    extra = (right - left) - table_w
    cols[1] = (cols[1][0], cols[1][1] + extra * 0.35)
    cols[8] = (cols[8][0], cols[8][1] + extra * 0.65)
    table_w = sum(w_ for _, w_ in cols)
    row_h = 5.05 * mm
    header_h = 6.1 * mm

    # header
    c.setFillColor(INK)
    c.rect(left, y - header_h, table_w, header_h, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont(FONT_B, 6.4)
    x = left
    for title, cw in cols:
        c.drawString(x + 1.6 * mm, y - header_h + 2.3 * mm, title.upper())
        x += cw
    y -= header_h

    for i, row in enumerate(ROWS):
        is_sum = row["kind"] == "summary"
        if is_sum:
            c.setFillColor(HexColor("#E4E8F2"))
        elif i % 2 == 0:
            c.setFillColor(white)
        else:
            c.setFillColor(HexColor("#F7F9FC"))
        c.rect(left, y - row_h, table_w, row_h, fill=1, stroke=0)

        dur = row["finish"] - row["start"] + 1
        st = status_of(row["pct"], row["finish"])
        vals = [
            row["id"],
            row["name"].split("  ", 1)[-1] if row["name"].startswith("F") else row["name"],
            fmt(week_start(row["start"])),
            fmt(week_end(row["finish"])),
            str(dur),
            row["pred"],
            f"{row['pct']} %",
            st,
            deliverable.get(row["id"], ""),
        ]
        x = left
        for (title, cw), val in zip(cols, vals):
            if title == "ID":
                c.setFillColor(INDIGO_DEEP)
                c.setFont(FONT_B, 6.2)
            elif title == "Estado":
                c.setFillColor(OK if st == "Completada" else (GOLD_DEEP if st == "En curso" else MUTED))
                c.setFont(FONT_B, 6.2)
            elif is_sum:
                c.setFillColor(INK)
                c.setFont(FONT_B, 6.3)
            else:
                c.setFillColor(INK)
                c.setFont(FONT, 6.3)
            c.drawString(x + 1.6 * mm, y - row_h + 2 * mm, val)
            x += cw
        y -= row_h

    c.setStrokeColor(LINE)
    c.setLineWidth(0.3)
    c.rect(left, y, table_w, header_h + row_h * len(ROWS), fill=0, stroke=1)

    y -= 6 * mm
    c.setFillColor(INK)
    c.setFont(FONT_B, 10)
    c.drawString(left, y, "Hitos de control")
    y -= 5.2 * mm

    ms_cols = [("ID", 16 * mm), ("Hito", 78 * mm), ("Fecha", 28 * mm), ("Sem.", 16 * mm), ("Estado", 28 * mm), ("Criterio de aceptación", 160 * mm)]
    c.setFillColor(INK)
    c.rect(left, y - 6.5 * mm, sum(w_ for _, w_ in ms_cols), 6.5 * mm, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont(FONT_B, 6.4)
    x = left
    for title, cw in ms_cols:
        c.drawString(x + 1.6 * mm, y - 4.4 * mm, title.upper())
        x += cw
    y -= 6.5 * mm

    criteria = {
        "M1": "Alcance escrito: simula y calcula; no mide certificado ni inyecta.",
        "M2": "CLI TAN genera Excel/PDF/BOM para casos small/medium/large.",
        "M3": "tests/test_dsp.py pasa contra el catálogo de señales patrón.",
        "M4": "Dashboard con Monitor, Diseño TAN y Banco 24 V sobre un proyecto común.",
        "M5": "FSM HIL con E-stop enclavado y physical_outputs_available = false.",
        "M6": "output/tpa/ + informe P08. CSV de pañol es PLUS, no bloquea.",
        "M7": "MEMORIA_TPA.md ensamblada (P12), lista para el guía.",
        "M8": "Defensa oral. Fecha 04-dic-2026: supuesto si no hay comisión.",
    }
    for i, ms in enumerate(MILESTONES):
        rh = 5.15 * mm
        c.setFillColor(white if i % 2 == 0 else HexColor("#F7F9FC"))
        c.rect(left, y - rh, sum(w_ for _, w_ in ms_cols), rh, fill=1, stroke=0)
        st = "Cumplido" if ms["date"] <= STATUS else "Pendiente"
        vals = [ms["id"], ms["name"], fmt(ms["date"]), f"S{ms['week']:02d}", st, criteria[ms["id"]]]
        x = left
        for (title, cw), val in zip(ms_cols, vals):
            if title == "Estado":
                c.setFillColor(OK if st == "Cumplido" else MUTED)
                c.setFont(FONT_B, 6.2)
            else:
                c.setFillColor(INK)
                c.setFont(FONT_B if title == "ID" else FONT, 6.3)
            c.drawString(x + 1.6 * mm, y - rh + 2 * mm, val)
            x += cw
        y -= rh

    c.showPage()


def wrap(c: canvas.Canvas, text: str, font: str, size: float, max_w: float) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if c.stringWidth(trial, font, size) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def draw_notes_page(c: canvas.Canvas) -> None:
    w, h = landscape(A3)
    c.setFillColor(BG)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    top = draw_header(c, w, h, "03  /  RUTA CRÍTICA, ALCANCE Y RIESGOS")
    draw_footer(c, w)

    left = 12 * mm
    right = w - 12 * mm
    gap = 6 * mm
    col_w = (w - 24 * mm - gap) / 2
    y = top - 4 * mm

    def card(x, y, cw, ch, title, body_fn):
        c.setFillColor(white)
        c.roundRect(x, y - ch, cw, ch, 3, fill=1, stroke=0)
        c.setFillColor(INDIGO_DEEP)
        c.rect(x, y - 7.5 * mm, cw, 7.5 * mm, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(x, y - 7.5 * mm, 2.2 * mm, 7.5 * mm, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(FONT_B, 8.5)
        c.drawString(x + 6 * mm, y - 5.1 * mm, title)
        body_fn(x, y - 12 * mm, cw)

    # left column cards
    def ruta(x, yy, cw):
        c.setFillColor(INK)
        c.setFont(FONT, 8)
        text = (
            "0.1 Alcance  →  0.2 Norma  →  2.1 Cálculos TAN  →  3.2 DSP/PLL  →  "
            "4.1 Monitor  →  5.1 Interlocks HIL  →  6.1 Evidencias  →  7.1 Memoria  →  7.4 Defensa."
        )
        lines = wrap(c, text, FONT, 8, cw - 12 * mm)
        for i, line in enumerate(lines):
            c.drawString(x + 6 * mm, yy - i * 3.6 * mm, line)
        c.setFillColor(MUTED)
        c.setFont(FONT, 7.5)
        note = (
            "La ruta crítica del TPA no es el producto 400 V: es la cadena problema eléctrico → "
            "señal patrón → cálculo auditable → lógica segura → evidencias → memoria. "
            "F2 y F3 ya cerraron. F7 (memoria) parte en S13; F6.3 (CSV pañol) no la bloquea."
        )
        nlines = wrap(c, note, FONT, 7.5, cw - 12 * mm)
        y2 = yy - (len(lines) + 1.4) * 3.6 * mm
        for i, line in enumerate(nlines):
            c.drawString(x + 6 * mm, y2 - i * 3.4 * mm, line)

    def avance(x, yy, cw):
        phases = [
            ("F0 Gestión", 86),
            ("F1 Arquitectura", 100),
            ("F2 TAN IEC 61439", 100),
            ("F3 DSP 3P+N", 100),
            ("F4 Operador / SCADA", 100),
            ("F5 SIL / HIL 24 V", 100),
            ("F6 Evidencias TPA", 51),
            ("F7 Memoria y defensa", 47),
        ]
        bar_x = x + 48 * mm
        bar_w = cw - 60 * mm
        for i, (name, pct) in enumerate(phases):
            py = yy - i * 5.4 * mm
            c.setFillColor(INK)
            c.setFont(FONT, 7.4)
            c.drawString(x + 6 * mm, py, name)
            c.setFillColor(PAPER)
            c.roundRect(bar_x, py - 0.6 * mm, bar_w, 3.2 * mm, 1, fill=1, stroke=0)
            color = INDIGO_DEEP if pct >= 100 else (GOLD_DEEP if pct >= 40 else PLAN)
            c.setFillColor(color)
            c.roundRect(bar_x, py - 0.6 * mm, bar_w * pct / 100, 3.2 * mm, 1, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont(FONT_B, 7)
            c.drawRightString(x + cw - 6 * mm, py, f"{pct}%")

    def fuera(x, yy, cw):
        items = [
            "Ensayo 380/400 VAC, 500 kW o ~700 A. Banco 48 V (KPS305D topea a 30 V).",
            "PWM, GPIO o contactores mandados por este software.",
            "Módulo de compensación 400/230 VAC o 50–100 A de producto.",
            "Medición con analizador de calidad de energía certificado / SEC.",
            "Inyección de corriente de compensación a la red.",
            "Hard real-time: Python sobre SO general no lo garantiza.",
            "Venta o conformidad de producto (licencia MIT académica).",
        ]
        c.setFont(FONT, 7.6)
        ty = yy
        for item in items:
            c.setFillColor(DANGER)
            c.circle(x + 8 * mm, ty + 1.1 * mm, 1.1 * mm, fill=1, stroke=0)
            c.setFillColor(INK)
            lines = wrap(c, item, FONT, 7.6, cw - 18 * mm)
            for i, line in enumerate(lines):
                c.drawString(x + 12 * mm, ty - i * 3.3 * mm, line)
            ty -= max(1, len(lines)) * 3.6 * mm + 1.2 * mm

    card(left, y, col_w, 48 * mm, "RUTA CRÍTICA DEL TPA", ruta)
    card(left, y - 52 * mm, col_w, 62 * mm, "AVANCE POR FASE (21-AGO-2026)", avance)
    card(left, y - 118 * mm, col_w, 58 * mm, "FUERA DE ALCANCE DEL TPA", fuera)

    rx = left + col_w + gap

    def supuestos(x, yy, cw):
        items = [
            "Calendario: 26 semanas, 08-jun-2026 a 06-dic-2026. Defensa 04-dic-2026 (supuesto).",
            "Autor único: Andres Barbudo Rodriguez. Institución: CFT Paillaco.",
            "Ritmo medido 21-ago: 6 de 16 prompts (P02–P07) en 2,5 h, 3 % Super Grok. No es el ritmo semanal.",
            "Plan restante: 2 sesiones/semana, 1–2 prompts. P08–P16 ≈ 4–6 h de Grok y ~5 % de cuota; el cuello no es la cuota.",
            "Pañol: wanptek KPS305D 0–30 V / 0–5 A y Gratten GA1102CAL. Clase A si hay 24 V vivos. 48 V fuera.",
            "HIL: physical_outputs_available = false. THDi no es SEC. CSV de 24 VDC = cadena de archivos, no H3.",
        ]
        c.setFont(FONT, 7.6)
        ty = yy
        for n, item in enumerate(items, 1):
            c.setFillColor(INDIGO_DEEP)
            c.setFont(FONT_B, 7.6)
            c.drawString(x + 6 * mm, ty, f"{n:02d}")
            c.setFillColor(INK)
            c.setFont(FONT, 7.6)
            lines = wrap(c, item, FONT, 7.6, cw - 18 * mm)
            for i, line in enumerate(lines):
                c.drawString(x + 14 * mm, ty - i * 3.3 * mm, line)
            ty -= max(1, len(lines)) * 3.5 * mm + 1.6 * mm

    def riesgos(x, yy, cw):
        rows = [
            ("R1", "Alcance se desliza a 400 V o hardware real", "Congelar M1. Prohibición de avance en docs."),
            ("R2", "DSP se vende como medición certificada", "THDi marcado académico; no IEC/SEC."),
            ("R3", "Python no cumple ciclo 12.8 kHz estable", "Procesamiento por microbloques; declarar límite."),
            ("R4", "HIL se confunde con banco físico", "Badge SIL y API physical_outputs_available=false."),
            ("R5", "Repetir el burst de 6 prompts y no escribir", "2 sesiones/semana; memoria P09–P12 en S13–S16."),
            ("R6", "Campaña pañol no se ejecuta (clase A / aula)", "PLUS. Defensa con sintético + procedimiento P06."),
        ]
        c.setFont(FONT, 7.2)
        ty = yy + 1 * mm
        for rid, risk, mit in rows:
            c.setFillColor(GOLD)
            c.roundRect(x + 6 * mm, ty - 2.4 * mm, 10 * mm, 5 * mm, 1, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont(FONT_B, 6.5)
            c.drawCentredString(x + 11 * mm, ty, rid)
            c.setFont(FONT_B, 7.2)
            c.drawString(x + 19 * mm, ty + 1.4 * mm, risk)
            c.setFont(FONT, 7)
            c.setFillColor(MUTED)
            c.drawString(x + 19 * mm, ty - 2.2 * mm, mit)
            ty -= 8.2 * mm

    def proximos(x, yy, cw):
        items = [
            "P08 (S12): casos de demo + informe de evidencias. Cierra M6.",
            "P09–P12 (S13–S16): memoria. Holgura hasta el paquete del 31-oct.",
            "P13–P14 (S16–S17): PPTX de defensa y banco de preguntas.",
            "Campaña CSV pañol 24 V si hay clase A (PLUS, no bloquea).",
            "P16 en noviembre: guion demo live (pañol o aula sin energía).",
            "No abrir diseño de potencia 400 V ni 48 V dentro del TPA.",
        ]
        c.setFont(FONT, 7.6)
        ty = yy
        for item in items:
            c.setFillColor(INDIGO)
            c.rect(x + 6 * mm, ty - 0.4 * mm, 2.4 * mm, 2.4 * mm, fill=1, stroke=0)
            lines = wrap(c, item, FONT, 7.6, cw - 18 * mm)
            c.setFillColor(INK)
            for i, line in enumerate(lines):
                c.drawString(x + 12 * mm, ty - i * 3.3 * mm, line)
            ty -= max(1, len(lines)) * 3.5 * mm + 1.8 * mm

    card(rx, y, col_w, 52 * mm, "SUPUESTOS DE PROGRAMACIÓN", supuestos)
    card(rx, y - 56 * mm, col_w, 62 * mm, "RIESGOS DEL CRONOGRAMA", riesgos)
    card(rx, y - 122 * mm, col_w, 54 * mm, "PRÓXIMOS 90 DÍAS (DESDE EL 21-AGO)", proximos)

    def lectura(x, yy, cw):
        bloques = [
            ("El % no es la memoria", "F1–F5 están cerradas. F7 vale la nota del TPA y parte en S13. Un 80 % de ingeniería no sustituye la defensa oral."),
            ("Línea de hoy", "S11 (21-ago) en oro. A la izquierda: ejecutado (P01–P07). A la derecha: P08–P16, guía y defensa del 04-dic (supuesto)."),
            ("Qué se defiende", "Cálculo TAN + DSP sobre patrón y SIL 24 V. No un AHF de 400 V ni un CSV de 24 VDC como prueba de H3."),
        ]
        bw = (cw - 18 * mm) / 3
        for i, (title, body) in enumerate(bloques):
            bx = x + 6 * mm + i * (bw + 3 * mm)
            c.setFillColor(INDIGO_DEEP)
            c.setFont(FONT_B, 8)
            c.drawString(bx, yy + 1 * mm, title)
            c.setFillColor(INK)
            c.setFont(FONT, 7.4)
            for j, line in enumerate(wrap(c, body, FONT, 7.4, bw - 2 * mm)):
                c.drawString(bx, yy - 4.2 * mm - j * 3.4 * mm, line)

    card(left, y - 180 * mm, right - left, 42 * mm, "CÓMO SE LEE ESTA CARTA EN LA DEFENSA", lectura)

    c.showPage()


def write_csv() -> None:
    with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["id", "nombre", "tipo", "semana_inicio", "semana_fin", "fecha_inicio", "fecha_fin", "duracion_sem", "predecesoras", "avance_pct", "estado"])
        for r in ROWS:
            w.writerow([
                r["id"], r["name"], r["kind"], r["start"], r["finish"],
                week_start(r["start"]).isoformat(), week_end(r["finish"]).isoformat(),
                r["finish"] - r["start"] + 1, r["pred"], r["pct"],
                status_of(r["pct"], r["finish"]),
            ])
        w.writerow([])
        w.writerow(["hito", "nombre", "semana", "fecha"])
        for ms in MILESTONES:
            w.writerow([ms["id"], ms["name"], ms["week"], ms["date"].isoformat()])


def write_md() -> None:
    gp = global_progress()
    lines = [
        "# Carta Gantt del TPA",
        "",
        "**Proyecto:** Controlador de borde para filtro activo de armónicos (AHF)",
        "**Repositorio:** `snocomm-edge-controller`",
        f"**Periodo:** {fmt(PROJECT_START)} — {fmt(PROJECT_END)} (26 semanas)",
        f"**Fecha de estado:** {fmt(STATUS)}",
        f"**Avance ponderado:** {gp} %",
        "",
        "Documento de programación del Trabajo Práctico Aplicado. El PDF de entrega es `CARTA_GANTT_TPA.pdf` (A3 apaisado, 3 láminas). El CSV `CARTA_GANTT_TPA.csv` importa a Excel o LibreOffice Calc (separador `;`).",
        "",
        "## Alcance que programa esta carta",
        "",
        "**Autor:** Andres Barbudo Rodriguez  ",
        "**Institución:** CFT Paillaco",
        "",
        "Preingeniería de tableros BT (IEC 61439 / TAN), DSP 3P+N sobre señales patrón y validación SIL del banco 24 V (KPS305D). **Hoy calcula y simula; no mide con instrumento certificado ni inyecta corriente.**",
        "",
        "## Gantt (Mermaid)",
        "",
        "```mermaid",
        "gantt",
        "    title TPA AHF Edge Controller — jun a dic 2026",
        "    dateFormat  YYYY-MM-DD",
        "    axisFormat  %d %b",
        "    todayMarker on",
        "    excludes    weekends",
        "",
        "    section F0 Gestion",
        "    Kickoff y alcance                 :done, 0_1, 2026-06-08, 14d",
        "    Revision normativa IEC/RIC        :done, 0_2, 2026-06-08, 28d",
        "    EDT, riesgos y carta Gantt        :done, 0_3, 2026-06-15, 14d",
        "",
        "    section F1 Arquitectura",
        "    Procesos IPC y supervisory        :done, 1_1, 2026-06-15, 21d",
        "    Docker, ADC y shared memory       :done, 1_2, after 1_1, 21d",
        "",
        "    section F2 TAN IEC 61439",
        "    Calculos I / Icw / calentamiento  :done, 2_1, 2026-06-22, 21d",
        "    CLI, XL3 y expediente             :done, 2_2, after 2_1, 21d",
        "    Tests de reglas TAN               :done, 2_3, 2026-07-13, 21d",
        "",
        "    section F3 DSP 3P+N",
        "    Generador de senales patron       :done, 3_1, 2026-07-06, 21d",
        "    Clarke, PLL, H3/H5/H7             :done, 3_2, 2026-07-13, 28d",
        "    Tests DSP y THDi academico        :done, 3_3, 2026-07-27, 21d",
        "",
        "    section F4 Operador y SCADA",
        "    Monitor AHF                       :done, 4_1, 2026-07-20, 28d",
        "    Vista TAN e importacion campana   :done, 4_2, 2026-08-03, 21d",
        "    Modbus TLS / Influx / proyecto    :done, 4_3, 2026-07-27, 28d",
        "",
        "    section F5 SIL HIL 24 V",
        "    FSM, E-stop e interlocks          :done, 5_1, 2026-08-10, 14d",
        "    Vista Banco 24 V y paquete panol  :done, 5_2, 2026-08-17, 7d",
        "    Criterios SIL y tests potencia    :done, 5_3, 2026-08-17, 7d",
        "",
        "    section F6 Evidencias",
        "    Regresion y casos demo            :active, 6_1, 2026-08-17, 14d",
        "    Informe de evidencias y limites   :6_2, 2026-08-24, 7d",
        "    Campana panol 24 V CSV            :active, 6_3, 2026-08-24, 49d",
        "",
        "    section F7 Memoria y defensa",
        "    Borrador de memoria P09-P12       :7_1, 2026-08-31, 28d",
        "    PPTX y preguntas P13-P14          :7_3, 2026-09-21, 14d",
        "    Revision del guia                 :7_2, 2026-09-28, 35d",
        "    Guion demo live P16               :7_5, 2026-11-02, 21d",
        "    Entrega y defensa TPA             :milestone, 7_4, 2026-12-04, 0d",
        "```",
        "",
        "## Hitos",
        "",
        "| ID | Hito | Fecha | Estado |",
        "|---|---|---|---|",
    ]
    for ms in MILESTONES:
        st = "Cumplido" if ms["date"] <= STATUS else "Pendiente"
        lines.append(f"| {ms['id']} | {ms['name']} | {fmt(ms['date'])} | {st} |")
    lines += [
        "",
        "## Ruta crítica",
        "",
        "`0.1 → 0.2 → 2.1 → 3.2 → 4.1 → 5.1 → 6.1 → 7.1 → 7.4`",
        "",
        "La ruta crítica del TPA es la cadena **problema eléctrico → señal patrón → cálculo auditable → lógica segura → evidencias → memoria**. No es el producto de 400 V. F6.3 (CSV pañol) es PLUS y no bloquea la memoria.",
        "",
        "## Ritmo medido (21-ago-2026)",
        "",
        "- 6 de 16 prompts (P02–P07) en **2,5 h** sin interrupciones.",
        "- Consumo Super Grok: **3 %**. Restan P08–P16 ≈ 4–6 h y ~5 % de cuota.",
        "- El plan semanal **no** copia ese burst: 2 sesiones/semana, 1–2 prompts.",
        "- Holgura: paquete de software+memoria el 31-oct; defensa 04-dic-2026 (supuesto).",
        "",
        "## Fuera de alcance",
        "",
        "- Ensayo 380/400 VAC, 500 kW, ~700 A o banco 48 V reales",
        "- PWM, GPIO o contactores mandados por este software",
        "- Medición con analizador certificado / SEC",
        "- Inyección de corriente y hard real-time",
        "",
        f"*Generado el {fmt(STATUS)}. Autor: Andres Barbudo Rodriguez — CFT Paillaco.*",
        "",
    ]
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    c = canvas.Canvas(str(PDF_PATH), pagesize=landscape(A3))
    c.setTitle("Carta Gantt TPA — AHF Edge Controller")
    c.setAuthor("Andres Barbudo Rodriguez")
    c.setSubject("Programación del Trabajo Práctico Aplicado")
    draw_gantt_page(c)
    draw_table_page(c)
    draw_notes_page(c)
    c.save()
    write_csv()
    write_md()
    print(f"PDF  {PDF_PATH}")
    print(f"CSV  {CSV_PATH}")
    print(f"MD   {MD_PATH}")
    print(f"Avance ponderado {global_progress()} %")


if __name__ == "__main__":
    main()
