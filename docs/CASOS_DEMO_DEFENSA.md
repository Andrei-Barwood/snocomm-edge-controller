# Casos de demostración para la defensa

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  
**Sin Docker.** Receta: `docs/run_demo_tpa.sh` o los comandos de cada caso.

El HIL y el pañol de este TPA son **24 VDC**. 48 V, 400 V de ensayo, 500 kW
y ~700 A están fuera. El THDi del Monitor es académico (Ih/I1 de H3+H5+H7),
no IEC/SEC.

| Caso | Vista | Qué demuestra | Qué no es |
|---|---|---|---|
| A | Monitor AHF | DSP sobre patrón `combined_it` | Medición de la red del CFT |
| B | Diseño TAN | Prediseño IEC 61439 (small) | Tablero construido o certificado |
| C | Banco 24 V (SIL) | FSM + `physical_outputs_available = false` | Fuente energizada por el software |

---

## Receta copy-paste (sin Docker)

Desde la raíz del repositorio:

```bash
# CASO A y C — dashboard
PYTHONPATH=. python hil_app.py
# Navegador: http://localhost:8080
# Vista Monitor AHF (A) · Vista Banco 24 V (C)

# CASO B — prediseño TAN small (no escribe en output/web/)
PYTHONPATH=. python -m tan_telecom --example small --output ./output/tpa/demo_defensa -v
```

`main_industrial.py` también arranca el stack de simulación; **para la
defensa basta `python hil_app.py`**. No hace falta Docker, Influx ni Modbus.

O: `bash docs/run_demo_tpa.sh` (genera el TAN small e imprime los comandos).

---

## CASO A — Patrón sintético `combined_it`

**Qué muestra:** Monitor AHF, PLL ~50 Hz, THDi académico, H3/H5/H7.  
**Origen:** `config_industrial.yaml` → `simulation.pattern: combined_it`
(`i1_peak` 100, `h3_peak` 20, `h5_peak` 10, `h7_peak` 5).  
**Arranque:** `PYTHONPATH=. python hil_app.py` → http://localhost:8080 → **Monitor AHF**.  
**Tests:** `tests/test_dsp.py` (`REL_TOL = 0.12`).

**Prohibido decir:** “medimos la red del CFT”. Tampoco: “este THDi sirve
para la SEC”, “el Gratten nos dio estos armónicos”.

### Narración oral (≈ 40 s)

1. “Este es el Monitor AHF. La señal no sale de un tablero del CFT: es el
   patrón sintético `combined_it` a 12,8 kHz por microbloques.”
2. “El PLL se traba a la **tensión** del PCC, no a la corriente. Debe
   leer cerca de 50 Hz.”
3. “H3 es secuencia cero y se suma en el neutro; H5 negativa; H7 positiva.
   Eso es lo que un AHF de 3P+N tendría que ver. Aquí no inyecto compensación.”
4. “El THDi del recuadro es Ih/I1 de H3+H5+H7, del orden de 23 %. Es
   académico. La tolerancia de los tests es 12 %.”
5. “Python sobre un SO general no es hard real-time. Lo declaro: el TPA
   calcula y simula; no mide con analizador certificado.”

### Captura sugerida

Pantalla Monitor AHF: KPI de THDi con la leyenda «Académico · no IEC/SEC»,
PLL ~50 Hz, barras H3/H5/H7. Sin CSV importado en esta toma.

### Pregunta trampa

**Profesor:** “¿Entonces mediste la red del CFT y ese THDi va a la SEC?”  
**Andres:** “No. Es un patrón de `dsp/patterns.py`. El THDi del dashboard
no es IEC 61000-4-7 ni evidencia SEC. Si mañana hay analizador certificado,
esa campaña se importa como CSV; hoy el DSP se defiende con el patrón.”

---

## CASO B — Diseño TAN (ejemplo **small**)

**Qué muestra:** Icw/Icc, calentamiento, envolvente XL³, Excel/PDF.  
**Arranque:**

```bash
PYTHONPATH=. python -m tan_telecom --example small --output ./output/tpa/demo_defensa -v
```

**Números reales de este comando** (no inventados): In base 75,97 A ·
selección **80 A** · Icc/Icw **16,0 / 16,0 kA** · ΔT **10,7 °C** (límite 30 °C) ·
XL³ **160** IP55 · forma **2b** · 45 kW, 4 racks, redundancia N.

La fórmula usa **400 V** como tensión de **cálculo** IEC 61439
(`In = P·1000 / (√3·V·cosφ·η)`). Eso no es un ensayo a 400 V.

Alternativa medium: `--example medium` (120 kW, 8 racks, N+1). En la
defensa basta **small**. Ya hay un small en `output/tpa/tan_small/`.

**Prohibido decir:** “este tablero está construido”. Tampoco: “está
certificado IEC 61439”, “lo ensayamos a 400 V en el pañol”.

### Narración oral (≈ 40 s)

1. “TAN-Telecom es preingeniería de tablero para un nodo telecom, no un
   tablero que yo haya armado.”
2. “Caso small: 45 kW, 4 racks. El código elige XL³ 160, forma 2b, 80 A
   de selección. Icw de catálogo cubre los 16 kA estimados.”
3. “El ΔT estimado es 10,7 °C. Eso es una regla de cálculo, no un ensayo
   de tipo de calentamiento.”
4. “Se genera Excel, PDF, HTML y BOM. El expediente es prediseño. Las
   verificaciones IEC 61439-1/2 las aplica el código; no tengo sello de
   laboratorio.”
5. “El 400 V de la fórmula es la barra de cálculo. El pañol del CFT es
   24 VDC. No mezclo las dos capas.”

### Captura sugerida

PDF o HTML de `output/tpa/demo_defensa/` (o `tan_small/`): tabla In / Icw /
ΔT / XL³. Segunda toma: vista **Diseño TAN** en http://localhost:8080.

### Pregunta trampa

**Profesor:** “¿Construiste y ensayaste este tablero?”  
**Andres:** “No. Es un prediseño. El test `tan_telecom/tests/` verifica el
cálculo. Un Excel/PDF no es certificación IEC 61439 ni memoria RIC de
obra.”

---

## CASO C — Banco SIL 24 V (simulado) + paquete de pañol 24 V

**Qué muestra:** POWER_OFF → SELF_TEST → PRECHARGE → READY → RUN, E-stop
enclavado, `physical_outputs_available = false`, `source_v = 24 V`, techo
30 V, 5 A / 120 W (mismos límites que la wanptek KPS305D). Abajo, el
paquete de pañol: KPS305D + Gratten GA1102CAL.

**Arranque:** mismo `python hil_app.py` → vista **Banco 24 V**.  
Botones: Iniciar autoprueba → Habilitar PWM HIL → Parada de emergencia.  
**Tests:** `tests/test_power_stage.py`, `docs/MATRIZ_SIL_TPA.md`.

El modelo **no es 48 V**. 48 V no cabe en la KPS305D (tope 30 V) y está
fuera del TPA.

**Prohibido decir:** “energizamos 48 V reales”. Tampoco: “el software
energiza la KPS305D”, “el PC manda el contactor”, “hay PWM de hardware”.

### Narración oral (≈ 40 s)

1. “Esta vista es la capa A: un HIL de 24 V / 120 W. Los indicadores de
   PWM y contactor son booleanos. `physical_outputs_available` es false
   siempre.”
2. “Arranco: POWER_OFF, autoprueba, precarga al 90 %, READY, y recién
   ahí habilito el PWM simulado. Si doy enable antes, el software
   rechaza.”
3. “E-stop enclava. No hay rearranque automático: hay que liberar y
   reset manual. El computador no anula ese latch.”
4. “Abajo está la capa B, el pañol: wanptek KPS305D a 24,0 V y Gratten
   GA1102CAL. Este programa no está cableado a la fuente. El corte físico
   es el switch I/O.”
5. “No hay 48 V en este TPA. Si me preguntan por 400 V: no hay medio de
   prueba en este CFT. La licencia clase A no reemplaza ese banco.”

### Captura sugerida

1. Vista Banco 24 V en RUN, badge «SIMULACIÓN · SIN SALIDAS FÍSICAS».  
2. Tras E-stop: estado ESTOP, salidas en false.  
3. Bloque pañol con las tres capas y KPS305D + GA1102CAL.

### Pregunta trampa

**Profesor:** “¿El Raspberry genera el PWM y energiza 48 V?”  
**Andres:** “No. El HIL es 24 V simulados. `physical_outputs_available`
es false. La KPS305D topea a 30 V: 48 V no cabe. El software no conmuta
la fuente.”

---

## Orden sugerido en la mesa (10 min)

| Min | Caso | Qué pulsar |
|---|---|---|
| 0–3 | A | Monitor AHF, señalar THDi académico y PLL |
| 3–6 | B | PDF small o vista Diseño TAN |
| 6–9 | C | Banco 24 V: start → enable → E-stop |
| 9–10 | Límite | “No medimos la red, no hay tablero construido, no hay 48 V ni 400 V de ensayo.” |

Campaña live con KPS305D + Gratten: procedimiento en
`docs/PROCEDIMIENTO_SCOPE_24V.md`. Solo con clase A. Un CSV de 24 VDC
prueba la cadena de archivos, **no** H3.

---

*Andres Barbudo Rodriguez — CFT Paillaco — 21-ago-2026*
