"""Árbol de problemas TPA — 24 V (KPS305D + GA1102CAL).

Reemplaza Arbol_problemas_proyecto_academico_Snocomm.pdf reutilizando
el layout y la paleta del generador del 7-ago-2026.
"""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


OUT = Path(
    "/Users/andreibarwood/Documents/CFT/2026/02 - Semestre 2/01 - TPA"
    "/Arbol_problemas_proyecto_academico_Snocomm.pdf"
)
W, H = landscape(A4)
M = 14 * mm

INK = colors.HexColor("#303030")
GRAPHITE = colors.HexColor("#4F4F4F")
PAPER = colors.HexColor("#F7F9FC")
MIST = colors.HexColor("#D7E0EC")
GOLD = colors.HexColor("#E3CA75")
GOLD_DARK = colors.HexColor("#CCB244")
INDIGO = colors.HexColor("#5A64BF")
INDIGO_DARK = colors.HexColor("#485199")
WHITE = colors.white
RED_SOFT = colors.HexColor("#F2D7D5")
LINE = colors.HexColor("#A8B3C1")

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_ITALIC = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"
pdfmetrics.registerFont(TTFont("Arial", FONT))
pdfmetrics.registerFont(TTFont("Arial-Bold", FONT_BOLD))
pdfmetrics.registerFont(TTFont("Arial-Italic", FONT_ITALIC))


def style(name, size=8.5, leading=None, color=INK, align=TA_LEFT, bold=False):
    return ParagraphStyle(
        name,
        fontName="Arial-Bold" if bold else "Arial",
        fontSize=size,
        leading=leading or size * 1.25,
        textColor=color,
        alignment=align,
        spaceAfter=0,
        spaceBefore=0,
    )


def safe(text):
    return escape(text).replace("\n", "<br/>")


def paragraph(c, text, x, y_top, width, pstyle, max_height=150 * mm):
    p = Paragraph(text, pstyle)
    _, height = p.wrap(width, max_height)
    p.drawOn(c, x, y_top - height)
    return height


def header(c, kicker, heading, subtitle, page):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(INDIGO_DARK)
    c.setFont("Arial-Bold", 8.5)
    c.drawString(M, H - 13 * mm, kicker.upper())
    c.setFillColor(INK)
    c.setFont("Arial-Bold", 22)
    c.drawString(M, H - 25 * mm, heading)
    paragraph(
        c,
        safe(subtitle),
        M,
        H - 31 * mm,
        W - 2 * M,
        style("subtitle", 9.1, 11.4, GRAPHITE),
    )
    c.setStrokeColor(MIST)
    c.setLineWidth(0.6)
    c.line(M, 9.5 * mm, W - M, 9.5 * mm)
    c.setFillColor(GRAPHITE)
    c.setFont("Arial", 6.8)
    c.drawString(
        M,
        5.5 * mm,
        "TPA CFT Paillaco · Andres Barbudo Rodriguez · banco 24 V (KPS305D + GA1102CAL)",
    )
    c.drawRightString(W - M, 5.5 * mm, f"{page} / 3")


def card(
    c,
    x,
    y,
    w,
    h,
    heading,
    body,
    fill=WHITE,
    border=INDIGO,
    heading_color=INK,
    body_color=INK,
    centered=False,
    heading_size=9.5,
    body_size=7.7,
):
    c.setFillColor(fill)
    c.setStrokeColor(border)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, 4 * mm, fill=1, stroke=1)
    pad = 5 * mm
    align = TA_CENTER if centered else TA_LEFT
    th = paragraph(
        c,
        safe(heading),
        x + pad,
        y + h - 4 * mm,
        w - 2 * pad,
        style("ct", heading_size, heading_size * 1.17, heading_color, align, True),
        h,
    )
    paragraph(
        c,
        safe(body),
        x + pad,
        y + h - 6 * mm - th,
        w - 2 * pad,
        style("cb", body_size, body_size * 1.25, body_color, align),
        h - th - 8 * mm,
    )


def line(c, x1, y1, x2, y2, width=1.8):
    c.setStrokeColor(INDIGO_DARK)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)


def draw_tree(c):
    header(
        c,
        "Árbol de problemas",
        "Problema académico que origina el proyecto",
        "El problema no es que 'falta una aplicación'; es que el diagnóstico, la preingeniería y la validación segura se realizan de forma fragmentada, y el CFT no dispone de medio de prueba a 48 V ni a 400 V.",
        1,
    )
    gap = 6 * mm
    col_w = (W - 2 * M - 2 * gap) / 3
    xs = [M + i * (col_w + gap) for i in range(3)]

    effects = [
        (
            "RIESGO TÉRMICO Y DE CONTINUIDAD",
            "Armónicos y corriente de neutro pueden aumentar pérdidas, temperatura, disparos y estrés sobre tableros, UPS, cables y transformadores.",
        ),
        (
            "DECISIONES DE TABLERO POCO TRAZABLES",
            "Se puede sobredimensionar, subdimensionar o documentar de forma incompleta corriente, envolvente, segregación, térmica y cortocircuito.",
        ),
        (
            "SALTO INSEGURO ENTRE TEORÍA Y HARDWARE",
            "Sin una clase de tensión que el pañol sí pueda energizar, el algoritmo queda sólo en simulación o se pretende un banco de 48/400 V que este CFT no puede ensayar.",
        ),
    ]
    causes = [
        (
            "CAUSAS ELÉCTRICAS Y DE INFORMACIÓN",
            "- Cargas TI no lineales y desequilibrio 3P+N\n"
            "- H3 de secuencia cero se suma en el neutro\n"
            "- Pocos datos de terreno y campañas cortas\n"
            "- El Gratten GA1102CAL no es analizador certificado\n"
            "- Un DC de 24 V no demuestra H3/H5/H7",
        ),
        (
            "CAUSAS METODOLÓGICAS",
            "- Cálculos, normas y medición tratados por separado\n"
            "- Hojas manuales y supuestos difíciles de auditar\n"
            "- Sin modelo común entre monitoreo y tablero\n"
            "- Poca trazabilidad requisito -> cálculo -> prueba\n"
            "- Cumplimiento confundido con predimensionamiento",
        ),
        (
            "CAUSAS DE PROTOTIPADO Y SEGURIDAD",
            "- Validar a 400 V no cabe en el CFT (sin ~700 A)\n"
            "- La KPS305D topea a 30 V: 48 V no es medio de prueba\n"
            "- Este software no genera PWM ni manda la fuente\n"
            "- Python/Linux no garantiza hard real-time\n"
            "- Scope de 2 canales; no hay 3P+N simultáneo",
        ),
    ]

    effect_y, effect_h = 128 * mm, 34 * mm
    center_y, center_h = 91 * mm, 28 * mm
    cause_y, cause_h = 28 * mm, 51 * mm
    cx = W / 2

    branch_top = 123 * mm
    line(c, cx, center_y + center_h, cx, branch_top)
    line(c, xs[0] + col_w / 2, branch_top, xs[2] + col_w / 2, branch_top)
    for x in xs:
        line(c, x + col_w / 2, branch_top, x + col_w / 2, effect_y)

    branch_bottom = 85 * mm
    line(c, cx, center_y, cx, branch_bottom)
    line(c, xs[0] + col_w / 2, branch_bottom, xs[2] + col_w / 2, branch_bottom)
    for x in xs:
        line(c, x + col_w / 2, branch_bottom, x + col_w / 2, cause_y + cause_h)

    for i, (h, b) in enumerate(effects):
        card(
            c,
            xs[i],
            effect_y,
            col_w,
            effect_h,
            h,
            b,
            GRAPHITE,
            GRAPHITE,
            WHITE,
            WHITE,
            True,
            9,
            7.4,
        )

    card(
        c,
        M + 42 * mm,
        center_y,
        W - 2 * M - 84 * mm,
        center_h,
        "ABORDAJE FRAGMENTADO, SIN MEDIO DE PRUEBA A 48/400 V",
        "En tableros BT de telecomunicaciones, medición, predimensionamiento IEC 61439 y validación segura no están integrados. El pañol del CFT Paillaco sí permite 24 VDC (wanptek KPS305D + Gratten GA1102CAL); 48 V y 400 V quedan fuera de este TPA.",
        INDIGO_DARK,
        INDIGO_DARK,
        WHITE,
        WHITE,
        True,
        10.4,
        8.0,
    )

    for i, (h, b) in enumerate(causes):
        card(
            c,
            xs[i],
            cause_y,
            col_w,
            cause_h,
            h,
            b,
            RED_SOFT,
            GOLD_DARK,
            INK,
            INK,
            False,
            9.2,
            7.35,
        )

    c.setFillColor(GRAPHITE)
    c.setFont("Arial-Italic", 6.8)
    c.drawCentredString(
        W / 2,
        17 * mm,
        "Efectos arriba - problema focal al centro - causas directas y estructurales abajo",
    )


def draw_formulation(c):
    header(
        c,
        "Formulación académica",
        "Cómo convertir el árbol en una propuesta defendible",
        "La plataforma responde al problema con cálculo, SIL y un ensayo a 24 V que sí cabe en el pañol. 48 V, 400 V y compensación a la red quedan fuera.",
        2,
    )
    card(
        c,
        M,
        114 * mm,
        126 * mm,
        43 * mm,
        "PLANTEAMIENTO DEL PROBLEMA",
        "Las instalaciones TI concentran cargas no lineales y H3 en el neutro. Sin una metodología integrada, armónicos, tablero y seguridad se estudian por separado. Pretender 48 V o 400 V en este CFT no es un medio de prueba: la KPS305D topea a 30 V.",
        MIST,
        INDIGO,
        INK,
        INK,
        heading_size=10.2,
        body_size=8.2,
    )
    card(
        c,
        M + 132 * mm,
        114 * mm,
        123 * mm,
        43 * mm,
        "PREGUNTA DE INVESTIGACIÓN",
        "¿Cómo puede una plataforma edge integrar análisis armónico 3P+N, predimensionamiento TAN (IEC 61439) y validación SIL de un banco 24 V contrastable con la wanptek KPS305D y el Gratten GA1102CAL del CFT Paillaco?",
        GOLD,
        GOLD_DARK,
        INK,
        INK,
        heading_size=10.2,
        body_size=8.2,
    )

    card(
        c,
        M,
        64 * mm,
        126 * mm,
        39 * mm,
        "OBJETIVO GENERAL",
        "Desarrollar y validar una plataforma académica que conecte DSP sobre señales patrón, preingeniería TAN y lógica SIL a 24 V / 120 W, con un ensayo de laboratorio en la KPS305D y captura CSV en el Gratten.",
        INDIGO_DARK,
        INDIGO_DARK,
        WHITE,
        WHITE,
        heading_size=10.2,
        body_size=8.2,
    )
    card(
        c,
        M + 132 * mm,
        64 * mm,
        123 * mm,
        39 * mm,
        "HIPÓTESIS DE TRABAJO",
        "Si el DSP sigue al patrón dentro de la tolerancia de tests/test_dsp.py y la FSM no rearma sola, el TPA cumple. El CSV de 24 VDC prueba la cadena fuente-scope-software, no H3. 48 V no se modela porque no se puede ensayar.",
        INDIGO,
        INDIGO,
        WHITE,
        WHITE,
        heading_size=10.2,
        body_size=8.0,
    )

    objectives = [
        ["Objetivos específicos", "Evidencia esperada"],
        [
            "1. Modelar señales y armónicos relevantes en 3P+N.",
            "Patrones dsp/patterns.py; tolerancia relativa 12 % en tests/test_dsp.py.",
        ],
        [
            "2. Contrastar el algoritmo de detección.",
            "THDi académico Ih/I1 de H3+H5+H7; no es evidencia IEC/SEC.",
        ],
        [
            "3. Predimensionar el tablero con supuestos explícitos.",
            "TAN-Telecom: Icw/Icc, XL3, Excel/PDF. No es tablero construido.",
        ],
        [
            "4. Validar secuencia SIL a 24 V, sin GPIO.",
            "FSM POWER_OFF→RUN, E-stop enclavado, physical_outputs_available = false.",
        ],
        [
            "5. Ensayar el banco físico de 24 V en el pañol.",
            "KPS305D 24,0 V / Ilim + Gratten GA1102CAL CSV. 48 V fuera.",
        ],
    ]
    tdata = []
    for ri, row in enumerate(objectives):
        tdata.append(
            [
                Paragraph(
                    cell,
                    style(
                        f"t{ri}",
                        6.9,
                        8.6,
                        WHITE if ri == 0 else INK,
                        TA_LEFT,
                        ri == 0,
                    ),
                )
                for cell in row
            ]
        )
    table = Table(tdata, colWidths=[125 * mm, 130 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("BACKGROUND", (0, 1), (-1, -1), WHITE),
                ("GRID", (0, 0), (-1, -1), 0.5, MIST),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    _, th = table.wrap(255 * mm, H)
    table.drawOn(c, M, 53 * mm - th)


def draw_pitch(c):
    header(
        c,
        "Presentación inicial",
        "Guion para proponerlo desde el comienzo de la clase",
        "Primero la necesidad eléctrica; después cada módulo y el límite honesto: 24 V sí, 48 V y 400 V no.",
        3,
    )
    card(
        c,
        M,
        107 * mm,
        133 * mm,
        50 * mm,
        "APERTURA DE 60 SEGUNDOS",
        "En tableros que alimentan servidores y telecomunicaciones, las cargas no lineales producen H3 que se suma en el neutro. El problema académico es estudiar por separado calidad de energía, tablero y seguridad. Mi TPA integra DSP, TAN y SIL a 24 V, contrastable con la wanptek KPS305D (0–30 V / 0–5 A) y el Gratten GA1102CAL del pañol. No compensa la red, no certifica un tablero y no ensaya 48 V: esa fuente topea a 30 V.",
        GOLD,
        GOLD_DARK,
        INK,
        INK,
        heading_size=10.5,
        body_size=8.2,
    )
    card(
        c,
        M + 139 * mm,
        107 * mm,
        116 * mm,
        50 * mm,
        "TÍTULO SUGERIDO",
        "Plataforma edge para preingeniería de tableros BT y validación SIL de un banco 24 V en infraestructura de telecomunicaciones\n\nVersión más acotada:\nDiseño y validación SIL a 24 V de una arquitectura edge para análisis armónico 3P+N (CFT Paillaco)",
        INDIGO_DARK,
        INDIGO_DARK,
        WHITE,
        WHITE,
        heading_size=10.5,
        body_size=8.2,
    )

    mapping = [
        ["Parte del problema", "Respuesta del proyecto", "Límite honesto"],
        [
            "Poca visibilidad de armónicos",
            "Monitor AHF: DSP Clarke, PLL, H3/H5/H7.",
            "Patrón sintético o CSV; THDi no es IEC/SEC.",
        ],
        [
            "Preingeniería fragmentada",
            "TAN: corriente, Icw/Icc, XL³, forma, Excel/PDF.",
            "Heurístico; no certifica IEC 61439.",
        ],
        [
            "Salto inseguro a 48/400 V",
            "Banco 24 V SIL + KPS305D/Gratten.",
            "El software no energiza la fuente. 48 V fuera.",
        ],
        [
            "Falta de integración",
            "Proyecto común: THDi, TAN y estado del banco.",
            "El DSP no manda el banco ni la KPS305D.",
        ],
    ]
    tdata = []
    for ri, row in enumerate(mapping):
        tdata.append(
            [
                Paragraph(
                    cell,
                    style(
                        f"m{ri}",
                        7.1,
                        8.8,
                        WHITE if ri == 0 else INK,
                        TA_LEFT,
                        ri == 0,
                    ),
                )
                for cell in row
            ]
        )
    table = Table(tdata, colWidths=[76 * mm, 101 * mm, 78 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("BACKGROUND", (0, 1), (-1, -1), WHITE),
                ("GRID", (0, 0), (-1, -1), 0.5, MIST),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    _, th = table.wrap(255 * mm, H)
    table.drawOn(c, M, 95 * mm - th)

    card(
        c,
        M,
        25 * mm,
        W - 2 * M,
        24 * mm,
        "CIERRE RECOMENDADO",
        "El resultado académico no será un filtro industrial ni un banco de 48 V. Será una ruta trazable: problema eléctrico -> señal patrón -> cálculo TAN -> lógica SIL 24 V -> ensayo KPS305D + Gratten. Ese alcance es evaluable en el pañol del CFT Paillaco.",
        INDIGO_DARK,
        INDIGO_DARK,
        WHITE,
        WHITE,
        True,
        10,
        8.2,
    )


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=landscape(A4))
    c.setTitle("Árbol de problemas - TPA 24 V CFT Paillaco")
    c.setAuthor("Andres Barbudo Rodriguez")
    c.setSubject("Formulación académica TPA · banco 24 V · KPS305D + GA1102CAL")
    draw_tree(c)
    c.showPage()
    draw_formulation(c)
    c.showPage()
    draw_pitch(c)
    c.save()
    print(OUT)


if __name__ == "__main__":
    build()
