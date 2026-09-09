const pptxgen = require("pptxgenjs");

const INK = "303030", CHARCOAL = "262626", GOLD = "CCB244", GOLD_PALE = "F3EDDD";
const INDIGO = "5A64BF", PAPER = "D7E0EC", WHITE = "FFFFFF", MUTED = "626975";
const DANGER = "8F3232";
const HEADER = "Arial", BODY = "Calibri";
const W = 13.3, H = 7.5, M = 0.55, CW = W - 2 * M, FH = 0.38;

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.author = "Andres Barbudo Rodriguez";
  pres.title = "TPA AHF Edge Controller — CFT Paillaco";
  pres.subject = "Defensa TPA Electricidad 2026";

  function footer(s, n) {
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: H - FH, w: W, h: 0.05, fill: { color: GOLD }, line: { color: GOLD } });
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: H - FH + 0.05, w: W, h: FH - 0.05, fill: { color: INK }, line: { color: INK } });
    s.addText("CFT PAILLACO  ·  Electricidad  ·  TPA 2026", {
      x: M, y: H - FH + 0.05, w: 7, h: FH - 0.05,
      fontSize: 10, fontFace: BODY, color: GOLD, valign: "middle", margin: 0
    });
    s.addText(`${String(n).padStart(2, "0")}  /  14`, {
      x: W - M - 1.6, y: H - FH + 0.05, w: 1.6, h: FH - 0.05,
      fontSize: 10, fontFace: BODY, color: GOLD, bold: true, align: "right", valign: "middle", margin: 0
    });
  }

  function title(s, eye, txt) {
    s.addShape(pres.shapes.RECTANGLE, { x: M, y: 0.32, w: 0.1, h: 0.85, fill: { color: GOLD }, line: { color: GOLD } });
    s.addText(eye, { x: M + 0.22, y: 0.32, w: CW, h: 0.26, fontSize: 11, fontFace: BODY, color: INDIGO, bold: true, charSpacing: 2, margin: 0 });
    s.addText(txt, { x: M + 0.22, y: 0.55, w: CW, h: 0.55, fontSize: 26, fontFace: HEADER, color: INK, bold: true, margin: 0 });
  }

  // 1 Portada
  {
    const s = pres.addSlide(); s.background = { color: CHARCOAL };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.22, h: H, fill: { color: GOLD }, line: { color: GOLD } });
    s.addText("CFT PAILLACO  ·  CARRERA ELECTRICIDAD", {
      x: 0.7, y: 1.3, w: 12, h: 0.35, fontSize: 14, fontFace: BODY, color: GOLD, bold: true, charSpacing: 2, margin: 0
    });
    s.addText("Trabajo Práctico Aplicado", {
      x: 0.7, y: 1.85, w: 12, h: 0.45, fontSize: 18, fontFace: BODY, color: PAPER, margin: 0
    });
    s.addText("Controlador de borde para el estudio\nde un filtro activo de armónicos", {
      x: 0.7, y: 2.4, w: 12, h: 1.5, fontSize: 28, fontFace: HEADER, color: WHITE, bold: true, margin: 0
    });
    s.addText("Cálculo TAN  ·  DSP 3P+N  ·  SIL 24 VDC", {
      x: 0.7, y: 4.1, w: 12, h: 0.4, fontSize: 16, fontFace: BODY, color: GOLD, margin: 0
    });
    s.addText("Andres Barbudo Rodriguez", {
      x: 0.7, y: 5.2, w: 12, h: 0.4, fontSize: 18, fontFace: HEADER, color: WHITE, bold: true, margin: 0
    });
    s.addText("CFT Paillaco  ·  2026", {
      x: 0.7, y: 5.6, w: 12, h: 0.35, fontSize: 16, fontFace: BODY, color: PAPER, margin: 0
    });
    s.addNotes("Buenos días. Soy Andres Barbudo Rodriguez, CFT Paillaco. Este TPA calcula y simula: TAN, DSP sobre patrón y SIL a 24 V. No es un AHF de 400 V.");
  }

  // 2 Problema
  {
    const s = pres.addSlide(); s.background = { color: WHITE };
    title(s, "01  |  PROBLEMA", "Armónicos 3P+N en tableros telecom");
    const cards = [
      ["H3", "Secuencia cero", "No se cancela entre fases. Se suma en el neutro."],
      ["H5", "Secuencia negativa", "Típica de rectificador de 6 pulsos."],
      ["H7", "Secuencia positiva", "También aparece en cargas no lineales."]
    ];
    cards.forEach((c, i) => {
      const x = M + i * 4.05;
      s.addShape(pres.shapes.RECTANGLE, { x, y: 1.7, w: 3.85, h: 3.4, fill: { color: PAPER }, line: { color: PAPER } });
      s.addShape(pres.shapes.RECTANGLE, { x, y: 1.7, w: 0.12, h: 3.4, fill: { color: GOLD }, line: { color: GOLD } });
      s.addText(c[0], { x: x + 0.35, y: 1.9, w: 3.3, h: 0.7, fontSize: 32, fontFace: HEADER, color: INDIGO, bold: true, margin: 0 });
      s.addText(c[1], { x: x + 0.35, y: 2.65, w: 3.3, h: 0.4, fontSize: 16, fontFace: BODY, color: INK, bold: true, margin: 0 });
      s.addText(c[2], { x: x + 0.35, y: 3.2, w: 3.3, h: 1.4, fontSize: 15, fontFace: BODY, color: MUTED, margin: 0 });
    });
    s.addText("Un AHF de cuatro ramas es la respuesta de producto. Este TPA no lo construye.", {
      x: M, y: 5.3, w: CW, h: 0.45, fontSize: 16, fontFace: BODY, color: INK, italic: true, margin: 0
    });
    footer(s, 2);
    s.addNotes("En tableros que alimentan racks, H3 se suma en el neutro. Yo no fabrico el filtro: estudio el fenómeno con cálculo, patrón y SIL 24 V.");
  }

  // 3 Alcance
  {
    const s = pres.addSlide(); s.background = { color: WHITE };
    title(s, "02  |  ALCANCE", "Qué sí  ·  qué no");
    s.addShape(pres.shapes.RECTANGLE, { x: M, y: 1.55, w: 6.0, h: 4.9, fill: { color: PAPER }, line: { color: PAPER } });
    s.addText("SÍ EN ESTE TPA", { x: M + 0.3, y: 1.7, w: 5.4, h: 0.4, fontSize: 14, fontFace: BODY, color: INDIGO, bold: true, margin: 0 });
    s.addText([
      { text: "Prediseño TAN IEC 61439", options: { bullet: true, breakLine: true } },
      { text: "DSP sobre patrón (H3/H5/H7, THDi Ih/I1)", options: { bullet: true, breakLine: true } },
      { text: "SIL 24 V / 120 W, salidas físicas false", options: { bullet: true, breakLine: true } },
      { text: "Pañol: KPS305D + Gratten, procedimiento", options: { bullet: true } }
    ], { x: M + 0.3, y: 2.2, w: 5.4, h: 3.8, fontSize: 16, fontFace: BODY, color: INK, paraSpaceAfter: 8, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: M + 6.3, y: 1.55, w: 6.0, h: 4.9, fill: { color: "F8E8E8" }, line: { color: "F8E8E8" } });
    s.addShape(pres.shapes.RECTANGLE, { x: M + 6.3, y: 1.55, w: 6.0, h: 0.7, fill: { color: DANGER }, line: { color: DANGER } });
    s.addText("NO HUBO ENSAYO A 400 V", { x: M + 6.5, y: 1.6, w: 5.6, h: 0.6, fontSize: 16, fontFace: HEADER, color: WHITE, bold: true, valign: "middle", margin: 0 });
    s.addText([
      { text: "380/400 VAC, 500 kW, ~700 A", options: { bullet: true, breakLine: true } },
      { text: "48 V (la KPS305D topea a 30 V)", options: { bullet: true, breakLine: true } },
      { text: "PWM / GPIO / tablero construido", options: { bullet: true, breakLine: true } },
      { text: "THDi como evidencia SEC", options: { bullet: true } }
    ], { x: M + 6.5, y: 2.45, w: 5.5, h: 3.6, fontSize: 16, fontFace: BODY, color: INK, paraSpaceAfter: 8, margin: 0 });
    footer(s, 3);
    s.addNotes("La lámina importante: no hubo ensayo a 400 V. Clase A no inventa el banco de 700 A. El TPA es 24 V.");
  }

  // 4 Medios
  {
    const s = pres.addSlide(); s.background = { color: WHITE };
    title(s, "03  |  PAÑOL", "Medios reales, fotos 21-ago-2026");
    const rows = [
      ["Fuente", "wanptek KPS305D", "0–30 V / 0–5 A  ·  punto 24,0 V  ·  Ilim  ·  techo 30 V"],
      ["Osciloscopio", "Gratten GA1102CAL", "100 MHz  ·  2 ch  ·  1 GSa/s  ·  CSV/BMP USB"],
      ["Segunda persona", "Licencia clase A", "Obligatoria si hay 24 V energizados (A5)"],
      ["No fotografiado", "No inventar", "2.ª fuente, sondas, generador, E-stop de seta"]
    ];
    rows.forEach((r, i) => {
      const y = 1.6 + i * 1.05;
      s.addShape(pres.shapes.RECTANGLE, { x: M, y, w: CW, h: 0.95, fill: { color: i % 2 ? PAPER : WHITE }, line: { color: PAPER } });
      s.addText(r[0], { x: M + 0.25, y, w: 2.6, h: 0.95, fontSize: 13, fontFace: BODY, color: INDIGO, bold: true, valign: "middle", margin: 0 });
      s.addText(r[1], { x: M + 2.9, y, w: 3.6, h: 0.95, fontSize: 16, fontFace: HEADER, color: INK, bold: true, valign: "middle", margin: 0 });
      s.addText(r[2], { x: M + 6.6, y, w: 5.5, h: 0.95, fontSize: 14, fontFace: BODY, color: MUTED, valign: "middle", margin: 0 });
    });
    s.addText("El TPA es 24 V. 48 V no cabe en la KPS305D.", {
      x: M, y: 5.85, w: CW, h: 0.35, fontSize: 15, fontFace: BODY, color: DANGER, bold: true, margin: 0
    });
    footer(s, 4);
    s.addNotes("Solo estos dos aparatos están fotografiados. No invento una segunda fuente. 48 V fuera.");
  }

  // 5 Arquitectura
  {
    const s = pres.addSlide(); s.background = { color: WHITE };
    title(s, "04  |  SOFTWARE", "Se defiende con python hil_app.py");
    s.addText("DAQ / patrón  →  DSP (αβ0, PLL, H3/H5/H7)  →  Monitor · TAN · Banco 24 V", {
      x: M, y: 1.55, w: CW, h: 0.5, fontSize: 16, fontFace: BODY, color: INK, margin: 0
    });
    const boxes = [["Monitor AHF", "Patrón o CSV"], ["Diseño TAN", "Prediseño 61439"], ["Banco 24 V", "SIL, sin GPIO"]];
    boxes.forEach((b, i) => {
      const x = M + i * 4.05;
      s.addShape(pres.shapes.RECTANGLE, { x, y: 2.3, w: 3.85, h: 2.2, fill: { color: INK }, line: { color: INK } });
      s.addText(b[0], { x: x + 0.2, y: 2.5, w: 3.45, h: 0.7, fontSize: 18, fontFace: HEADER, color: GOLD, bold: true, margin: 0 });
      s.addText(b[1], { x: x + 0.2, y: 3.3, w: 3.45, h: 0.8, fontSize: 16, fontFace: BODY, color: PAPER, margin: 0 });
    });
    s.addText("Python sobre SO general no es hard real-time. Docker / Modbus / Influx: capacidad, no requisito.", {
      x: M, y: 4.8, w: CW, h: 0.7, fontSize: 15, fontFace: BODY, color: MUTED, margin: 0
    });
    footer(s, 5);
    s.addNotes("Abro hil_app en el puerto 8080. Tres vistas. No necesito Docker para defender.");
  }

  // 6 TAN
  {
    const s = pres.addSlide(); s.background = { color: WHITE };
    title(s, "05  |  TAN SMALL", "Un número real del repo");
    const stats = [["80 A", "In selección"], ["16 kA", "Icw / Icc"], ["10,7 °C", "ΔT estimado"], ["XL³ 160", "Forma 2b"]];
    stats.forEach((st, i) => {
      const x = M + i * 3.05;
      s.addShape(pres.shapes.RECTANGLE, { x, y: 1.7, w: 2.9, h: 2.5, fill: { color: PAPER }, line: { color: PAPER } });
      s.addText(st[0], { x, y: 1.95, w: 2.9, h: 1.1, fontSize: 28, fontFace: HEADER, color: INDIGO, bold: true, align: "center", margin: 0 });
      s.addText(st[1], { x: x + 0.1, y: 3.15, w: 2.7, h: 0.6, fontSize: 14, fontFace: BODY, color: INK, align: "center", margin: 0 });
    });
    s.addText("Caso small: 45 kW, 4 racks. 400 V es tensión de cálculo, no ensayo de pañol.\nNo es un tablero construido ni certificado IEC 61439.", {
      x: M, y: 4.5, w: CW, h: 1.2, fontSize: 16, fontFace: BODY, color: INK, margin: 0
    });
    footer(s, 6);
    s.addNotes("Muestro el PDF small: 80 A, 16 kA, XL3 160. Prediseño. No lo armé en taller.");
  }

  // 7 DSP
  {
    const s = pres.addSlide(); s.background = { color: WHITE };
    title(s, "06  |  DSP", "THDi académico, tolerancia 12 %");
    s.addShape(pres.shapes.RECTANGLE, { x: M, y: 1.6, w: 4.2, h: 4.6, fill: { color: INK }, line: { color: INK } });
    s.addText("≈ 23 %", { x: M + 0.2, y: 2.1, w: 3.8, h: 1.4, fontSize: 40, fontFace: HEADER, color: GOLD, bold: true, align: "center", margin: 0 });
    s.addText("THDi = Ih/I1\nH3+H5+H7  ·  combined_it", { x: M + 0.2, y: 3.6, w: 3.8, h: 1.4, fontSize: 16, fontFace: BODY, color: PAPER, align: "center", margin: 0 });
    s.addText([
      { text: "PLL sobre tensión del PCC, no sobre corriente", options: { bullet: true, breakLine: true } },
      { text: "H3 cero (neutro), H5 negativa, H7 positiva", options: { bullet: true, breakLine: true } },
      { text: "REL_TOL = 0.12 en tests/test_dsp.py", options: { bullet: true, breakLine: true } },
      { text: "No es IEC 61000-4-7 ni SEC", options: { bullet: true } }
    ], { x: M + 4.6, y: 1.8, w: 7.4, h: 4.2, fontSize: 18, fontFace: BODY, color: INK, paraSpaceAfter: 10, margin: 0 });
    footer(s, 7);
    s.addNotes("El número grande es Ih sobre I1 del patrón. Doce por ciento de tolerancia. No lo lleven a la SEC.");
  }

  // 8 Demo monitor
  {
    const s = pres.addSlide(); s.background = { color: WHITE };
    title(s, "07  |  DEMO A", "Monitor AHF — patrón sintético");
    s.addText("python hil_app.py  →  http://localhost:8080  →  Monitor AHF", {
      x: M, y: 1.55, w: CW, h: 0.4, fontSize: 16, fontFace: BODY, color: INDIGO, margin: 0
    });
    s.addText("Qué muestro: PLL ~50 Hz, H3/H5/H7, THDi académico.\nQué no digo: “medimos la red del CFT”.", {
      x: M, y: 2.15, w: CW, h: 1.3, fontSize: 20, fontFace: BODY, color: INK, margin: 0
    });
    s.addShape(pres.shapes.RECTANGLE, { x: M, y: 3.7, w: CW, h: 1.9, fill: { color: GOLD_PALE }, line: { color: GOLD_PALE } });
    s.addText("El Gratten no genera este espectro. combined_it está en dsp/patterns.py.", {
      x: M + 0.35, y: 4.15, w: CW - 0.7, h: 1.1, fontSize: 18, fontFace: BODY, color: INK, margin: 0
    });
    footer(s, 8);
    s.addNotes("En vivo dejo el Monitor con combined_it. Si preguntan por la red del CFT, digo que no.");
  }

  // 9 Banco SIL
  {
    const s = pres.addSlide(); s.background = { color: WHITE };
    title(s, "08  |  DEMO C", "Banco SIL 24 V — sin salidas físicas");
    const steps = ["POWER_OFF", "SELF_TEST", "PRECHARGE", "READY", "RUN"];
    steps.forEach((name, i) => {
      const x = M + i * 2.45;
      s.addShape(pres.shapes.RECTANGLE, { x, y: 1.7, w: 2.3, h: 1.1, fill: { color: INDIGO }, line: { color: INDIGO } });
      s.addText(name, { x, y: 1.7, w: 2.3, h: 1.1, fontSize: 12, fontFace: BODY, color: WHITE, bold: true, align: "center", valign: "middle", margin: 0 });
    });
    s.addText("physical_outputs_available = false  ·  source_v = 24 V  ·  techo 30 V\nE-stop enclavado. El PC no energiza la KPS305D. No hay 48 V.", {
      x: M, y: 3.2, w: CW, h: 1.5, fontSize: 18, fontFace: BODY, color: INK, margin: 0
    });
    footer(s, 9);
    s.addNotes("Pulso start, enable, estop. Señalo el flag false. Si dicen 48 V, recuerdo el tope de 30 V.");
  }

  // 10 Live pañol
  {
    const s = pres.addSlide(); s.background = { color: WHITE };
    title(s, "09  |  CASO D", "Live pañol o aula sin energía");
    s.addText("Sede A: 24,0 V  ·  Ilim 0,50 A  ·  CH1 Mean  ·  CSV USB  ·  clase A\nSede B: fotos de placa + BMP. “Hoy no hay 24 V vivos.”", {
      x: M, y: 1.6, w: CW, h: 1.3, fontSize: 18, fontFace: BODY, color: INK, margin: 0
    });
    s.addShape(pres.shapes.RECTANGLE, { x: M, y: 3.15, w: CW, h: 2.3, fill: { color: GOLD_PALE }, line: { color: GOLD_PALE } });
    s.addText("Frase obligatoria:\nesto demuestra la cadena fuente–scope–CSV–software.\nNo demuestra H3 ni la red del CFT.", {
      x: M + 0.35, y: 3.35, w: CW - 0.7, h: 1.95, fontSize: 18, fontFace: BODY, color: INK, margin: 0
    });
    footer(s, 10);
    s.addNotes("Si hay pañol y clase A, 24 V con Ilim primero. Si es aula, fotos. El CSV no es H3.");
  }

  // 11 Evidencias
  {
    const s = pres.addSlide(); s.background = { color: WHITE };
    title(s, "10  |  TESTS", "pytest tests tan_telecom/tests");
    const ev = [
      ["DSP", "test_dsp.py", "Patrones, REL_TOL 12 %"],
      ["TAN", "tan_telecom/tests", "Small 80 A, PDF"],
      ["SIL", "test_power_stage.py", "Latch, flag false"],
      ["Humo", "test_tpa_smoke.py", "Camino de defensa"]
    ];
    ev.forEach((e, i) => {
      const x = M + (i % 2) * 6.15, y = 1.6 + Math.floor(i / 2) * 2.15;
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 5.95, h: 2.0, fill: { color: PAPER }, line: { color: PAPER } });
      s.addText(e[0], { x: x + 0.3, y: y + 0.25, w: 5.3, h: 0.4, fontSize: 14, fontFace: BODY, color: INDIGO, bold: true, margin: 0 });
      s.addText(e[1], { x: x + 0.3, y: y + 0.7, w: 5.3, h: 0.45, fontSize: 18, fontFace: HEADER, color: INK, margin: 0 });
      s.addText(e[2], { x: x + 0.3, y: y + 1.2, w: 5.3, h: 0.45, fontSize: 14, fontFace: BODY, color: MUTED, margin: 0 });
    });
    footer(s, 11);
    s.addNotes("La evidencia es pytest archivado en output/tpa. A5 no es un assert: es clase A en el pañol.");
  }

  // 12 Límites
  {
    const s = pres.addSlide(); s.background = { color: WHITE };
    title(s, "11  |  LÍMITES", "Lo que no afirmo");
    s.addText([
      { text: "No hay medición certificada ni THDi SEC.", options: { bullet: true, breakLine: true } },
      { text: "No hay PWM real ni 48 V ni ensayo 400 V.", options: { bullet: true, breakLine: true } },
      { text: "Python no es hard real-time.", options: { bullet: true, breakLine: true } },
      { text: "TAN no está construido. Campaña CSV firmada: pendiente.", options: { bullet: true, breakLine: true } },
      { text: "Clase A ≠ banco de ~700 A.", options: { bullet: true } }
    ], { x: M, y: 1.6, w: CW, h: 4.8, fontSize: 20, fontFace: BODY, color: INK, paraSpaceAfter: 10, margin: 0 });
    footer(s, 12);
    s.addNotes("Cierro límites en voz alta para que no me los pregunten como trampa. Ya los dije yo.");
  }

  // 13 Conclusión
  {
    const s = pres.addSlide(); s.background = { color: WHITE };
    title(s, "12  |  CIERRE", "Hipótesis cumplida en software");
    s.addText("Si el DSP sigue al patrón (12 %) y la FSM no rearma sola, el TPA cumple.", {
      x: M, y: 1.65, w: CW, h: 1.1, fontSize: 20, fontFace: BODY, color: INK, margin: 0
    });
    s.addText("Trabajo futuro, fuera de este TPA: MCU/PWM a 24 V; analizador certificado; un TPA nuevo si hay medio de 400 V. El siguiente paso no es 500 kW en el CFT.", {
      x: M, y: 2.9, w: CW, h: 1.8, fontSize: 16, fontFace: BODY, color: MUTED, margin: 0
    });
    footer(s, 13);
    s.addNotes("No vendo 500 kW. Futuro: 24 V con MCU, o un TPA distinto si aparece banco de 400 V.");
  }

  // 14 Cierre
  {
    const s = pres.addSlide(); s.background = { color: CHARCOAL };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.22, h: H, fill: { color: GOLD }, line: { color: GOLD } });
    s.addText("Gracias", { x: 0.7, y: 2.2, w: 12, h: 1.0, fontSize: 40, fontFace: HEADER, color: WHITE, bold: true, margin: 0 });
    s.addText("Andres Barbudo Rodriguez", { x: 0.7, y: 3.4, w: 12, h: 0.45, fontSize: 22, fontFace: HEADER, color: GOLD, margin: 0 });
    s.addText("CFT Paillaco  ·  2026", { x: 0.7, y: 3.95, w: 12, h: 0.4, fontSize: 18, fontFace: BODY, color: PAPER, margin: 0 });
    s.addText("Preguntas", { x: 0.7, y: 5.0, w: 12, h: 0.4, fontSize: 16, fontFace: BODY, color: GOLD, margin: 0 });
    s.addNotes("Dejo la lámina de cierre y abro preguntas. Si piden 400 V, leo el alcance congelado.");
  }

  await pres.writeFile({ fileName: "docs/memoria/DEFENSA_TPA.pptx" });
  console.log("OK docs/memoria/DEFENSA_TPA.pptx");
})();
