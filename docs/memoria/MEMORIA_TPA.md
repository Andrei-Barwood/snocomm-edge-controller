# Trabajo Práctico Aplicado

**Título:** Controlador de borde para el estudio de un filtro activo de armónicos (AHF): cálculo TAN, DSP 3P+N y validación SIL a 24 VDC

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  
**Carrera:** Electricidad  
**Año:** 2026

Un solo autor. Nada más en esta línea.

El alcance congelado prima sobre esta portada: `docs/ALCANCE_TPA_CFT_PAILLACO.md`.  
Banco físico y modelo HIL: **24 VDC**. 48 V, 380/400 VAC, 500 kW y ~700 A
quedan fuera de este TPA.

---

# Índice

1. Planteamiento y alcance  
2. Marco normativo usado  
3. Arquitectura del software de borde  
4. Preingeniería TAN  
5. DSP 3P+N sobre señales patrón  
6. SIL del banco y aproximación 24 V en pañol  
7. Evidencias, límites y conclusiones  
8. Anexos (Gantt, inventario, bitácora, matriz SIL)

Anexo de trabajo futuro, **fuera de este TPA** (si se escribe): MCU/PWM
sobre 24 V u otros desarrollos. **No** hay capítulo de producto
50–100 A / 400 V como objetivo de este trabajo.

Cada capítulo debe leerse en 5–8 minutos (TPA de CFT, no tesis).

---

# 1. Planteamiento y alcance

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

Este TPA nace de un problema eléctrico concreto, no de un producto que
yo pretenda vender. En tableros de baja tensión que alimentan nodos de
telecomunicaciones —racks con fuentes conmutadas, cargas monofásicas,
algo de desequilibrio— aparecen armónicos. El 3.º (H3) es de secuencia
cero: no se cancela entre fases y se **suma en el neutro**. H5 es de
secuencia negativa; H7, de secuencia positiva. Un filtro activo de
armónicos (AHF) de cuatro ramas (3P+N) es la respuesta de industria a
ese fenómeno.

En el CFT Paillaco yo no construyo ese filtro. No hay banco para ensayar
~700 A a 380/400 V ni 500 kW. La licencia clase A de un profesional
asistente habilita trabajos de BT en otro contexto; **no reemplaza** el
medio de prueba que este CFT no tiene. No es cobardía: es el pañol que
fotografié el 21-ago-2026.

Lo que sí cabe aquí, y es lo que entrega este TPA, son tres capas:

1. **Cálculo** de tablero BT: preingeniería IEC 61439 con TAN-Telecom
   (corriente, Icw/Icc, calentamiento, forma, envolvente XL³, expediente
   Excel/PDF).
2. **DSP** sobre señales patrón 3P+N: Clarke αβ0, PLL sobre la tensión
   del PCC, extracción H3/H5/H7 y THDi académico Ih/I1, a 12,8 kHz por
   microbloques.
3. **Lógica segura** de un banco **simulado a 24 V / 120 W** (máquina de
   estados, E-stop enclavado, sin salidas físicas) y un procedimiento de
   laboratorio a **24 VDC** con la wanptek KPS305D (0–30 V / 0–5 A, punto
   24,0 V) y el Gratten GA1102CAL (100 MHz, 2 canales, CSV USB).

El fenómeno se estudia. La compensación **no** se inyecta a la red. El
software no genera PWM ni manda contactores. El HIL declara
`physical_outputs_available = false` siempre. La KPS305D topea a 30 V:
48 V no es medio de prueba de este TPA.

## Objetivo general

Demostrar, con archivos y tests de este repositorio, que un CFT puede
aproximar el problema 3P+N con cálculo auditable, DSP sobre patrón y
SIL a 24 V, sin fingir un ensayo industrial que el pañol no permite.

## Objetivos específicos (medibles)

1. El DSP de `tests/test_dsp.py` sigue a los patrones de
   `dsp/patterns.py` con `REL_TOL = 0.12`.
2. TAN-Telecom genera un prediseño small/medium con Icw, ΔT y XL³, y
   `tan_telecom/tests/` pasa.
3. La FSM de `power_stage/controller.py` llega a RUN y no rearma sola
   tras E-stop u OVERCURRENT; el flag de salidas físicas es false.
4. Tres vistas (Monitor, TAN, Banco 24 V) arrancan con
   `python hil_app.py`, sin Docker.
5. El pañol queda documentado (inventario, procedimiento, protocolo,
   bitácora). La campaña CSV firmada es PLUS, no requisito: un DC de
   24 V no prueba H3.

## Hipótesis de trabajo

Si el DSP sigue a la señal patrón dentro de la tolerancia de
`tests/test_dsp.py` y la FSM no rearma sola, el TPA cumple. El CSV del
Gratten, cuando exista, demuestra la cadena de archivos (Mean ≈ 24 V),
no el espectro.

El alcance está congelado en `docs/ALCANCE_TPA_CFT_PAILLACO.md`. No se
abre a 400 V sin un TPA nuevo.

---

*Andres Barbudo Rodriguez — CFT Paillaco*

---

# 2. Marco normativo usado

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

Este capítulo es literal: qué **aplica el código**, no qué “cumple el
equipo”. Ningún aparato de este TPA está certificado.

## IEC 61439-1/2

`tan_telecom/calculations.py` y `rules.py` usan la norma como **regla de
cálculo**: In, normalización de corriente, Icw/Icc de catálogo XL³,
estimación de calentamiento (referencia a §10.10 como estimación, no
como ensayo de tipo), forma de separación IEC 61439-2, tabla de
verificaciones Anexo D.

Lo que el código **no** hace: ensayo de tablero en laboratorio, sello de
ensamblador, certificación de producto.

## RIC

Solo se cita el párrafo que el proyecto escribe cuando hay carga
armónica: **RIC 04 p.5.3** (neutro al menos 50 % mayor que las fases con
cargas no lineales, salvo excepción de filtro en la carga). Está en
`project_store.py` (`ric04_neutral_note`) y pasa al Excel/PDF TAN si
`carga_armonica` es verdadera. El caso **small** de entrega (sin flag
armónico) no dispara esa nota.

## IEC 62477-1 e ISO 13850

Criterio de **diseño** del SIL (convertidor / E-stop): latch, no
rearranque automático, salidas lógicas a false. No hay certificado
62477 ni de parada de emergencia de seta (no fotografiada). El corte
físico del pañol es el switch I/O de la KPS305D.

## IEC 61000

Fuera de alcance de medición. El Gratten no es analizador. El THDi del
dashboard no es 61000-4-7.

## Tabla requisito | tratamiento | vacío

| Requisito | Cómo lo trata este TPA | Vacío |
|---|---|---|
| IEC 61439-1/2 cálculo In, Icw, forma, XL³ | `tan_telecom` aplica la regla | Ensayo de tipo, tablero construido |
| IEC 61439 §10.10 calentamiento | ΔT estimado en código | Ensayo de elevación de temperatura |
| RIC 04 p.5.3 neutro | Nota en prediseño si hay armónicos | Memoria RIC de obra |
| IEC 62477-1 / ISO 13850 | Latch SIL, E-stop lógico | Certificado de convertidor / seta física |
| IEC 61000 (EMC, 4-7) | Declarado fuera | Medición certificada |
| SEC | No se afirma conformidad | Informe SEC |

---

*Andres Barbudo Rodriguez — CFT Paillaco*

---

# 3. Arquitectura del software de borde

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

La defensa de **este** TPA no usa Docker. Se sostiene con:

```bash
python hil_app.py
```

y el navegador en http://localhost:8080 (Monitor AHF, Diseño TAN, Banco
24 V). `main_industrial.py` levanta el stack largo (DAQ, DSP, supervisory,
Modbus TLS, Influx). Eso es **capacidad**, no requisito.

## Tres procesos (stack industrial, opcional)

El README lo describe así:

1. **DAQ / generador de señales** — hardware o patrón sintético hacia
   memoria compartida (`SharedMemory`).
2. **DSP por microbloques** — 12,8 kHz, bloques de 128; Clarke αβ0, PLL,
   H3/H5/H7; telemetría a una cola. Un proyecto común (`/api/project`)
   comparte THDi, TAN y fallas del banco.
3. **Supervisory** — WebSocket, Influx, Modbus TCP/TLS.

```text
DAQ / patrón  →  SharedMemory  →  DSP (αβ0, PLL, H3/H5/H7)
                                        ↓
                                 cola de telemetría
                                        ↓
                              supervisory / hil_app.py
                              Monitor · TAN · Banco 24 V
```

Python sobre un SO general **no** garantiza hard real-time (frase del
README). El procesamiento es por microbloques; no se afirma ciclo
industrial cerrado.

`hil_app.py` es el recorte HIL: misma UI, sin Modbus ni Influx. El banco
es simulación (`physical_outputs_available = false`) y no conmuta la
KPS305D.

---

*Andres Barbudo Rodriguez — CFT Paillaco*

---

# 4. Preingeniería TAN

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

TAN-Telecom prediseña tableros para nodos telecom. **No se construyó
ningún tablero en este TPA.**

**Entradas:** potencia kW, número de racks, redundancia (N / N+1 / 2N),
IP mínimo, flags de carga armónica y sísmico.

**Reglas:** `calculations.py` (In, Icw/Icc, ΔT) y `rules.py` (familia
TT-S/M/E, forma IEC 61439-2, envolvente XL³, verificaciones Anexo D, BOM).

**Salidas:** Excel, PDF, HTML, Markdown, JSON, CSV de BOM.

Comando de defensa (no escribe en `output/web/`):

```bash
PYTHONPATH=. python -m tan_telecom --example small --output ./output/tpa/demo_defensa -v
```

## Caso real del repo: small

Artefacto: `output/tpa/tan_small/TT-S-20260821-154807_memoria.md`.

| Parámetro | Valor del archivo |
|---|---|
| Potencia / racks / redundancia | 45,0 kW · 4 · N |
| In base / selección | 75,97 A / **80,0 A** |
| Icc / Icw | **16,0 / 16,0 kA** |
| ΔT estimado | **10,7 °C** (límite 30,0 °C) |
| Envolvente | XL³ 160 IP55 |
| Forma | 2b (familia TT-S) |

La fórmula usa `V = 400 V` como tensión de **cálculo**
(`In = P·1000/(√3·V·cosφ·η)`). Eso no es un ensayo a 400 V en el pañol.

`carga_armonica` es false en este small: no aparece la nota RIC 04 p.5.3.
Esa nota sí sale en un medium con el flag armónico (`project_store.py`).

Los tests `tan_telecom/tests/test_calculations.py` y `test_rules.py`
verifican el cálculo, no un tablero de laboratorio.

---

*Andres Barbudo Rodriguez — CFT Paillaco*

---

# 5. DSP 3P+N sobre señales patrón

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

Un profesor de electricidad puede seguir este capítulo sin abrir el
código. El DSP vive en `dsp/core.py`. Los patrones, en `dsp/patterns.py`.
La prueba, en `tests/test_dsp.py` con **`REL_TOL = 0.12` (12 %)**.

## Por qué 3P+N y secuencia cero

En un sistema trifásico equilibrado, las fundamentales se cancelan en el
neutro. H3 es de **secuencia cero**: las tres fases van al mismo tiempo
y el neutro lleva aproximadamente **tres veces** esa componente. Por eso
un AHF de telecomunicaciones se piensa con cuatro ramas. Este TPA no
inyecta esa compensación; solo la calcula sobre una señal que **conoce**.

## Clarke αβ0, PLL y armónicos

Clarke pasa abc a αβ0. El eje 0 carga la secuencia cero (H3). El PLL se
traba a la **tensión del PCC**, no a la corriente (`test_pll_locks_to_voltage_not_current`).
Sobre el marco síncrono se extraen H3 (cero), H5 (negativa) y H7 (positiva).

THDi académico: `100 · Ih / I1`, con Ih de H3+H5+H7. No es IEC 61000-4-7
ni SEC. El test `test_thdi_uses_fundamental_not_total_rms` impide usar el
RMS total como denominador.

Muestreo: 12,8 kHz por microbloques de 128 muestras. Python no es hard
real-time.

## Catálogo de patrones

| Patrón | Qué verifica el test |
|---|---|
| `fundamental_only` | I1 sin armónicos |
| `zero_sequence_neutral` | H3 y neutro ≈ 3·I0 |
| `negative_sequence_h5` | H5 |
| `positive_sequence_h7` | H7 |
| `combined_it` | I1+H3+H5+H7, demo del Monitor (THDi ≈ 22,9 %) |
| `pll_voltage_vs_current` | PLL sigue tensión, no corriente |

## CSV del Gratten GA1102CAL

El osciloscopio tiene **2 canales**. No captura 3P+N a la vez. No es
analizador de red. Un CSV de pañol 24 VDC se importa con **CH1 → va**.

**Campaña física pendiente.** El procedimiento está en
`docs/PROCEDIMIENTO_SCOPE_24V.md`. El archivo
`acquisition/panol_24v_gratten_example.csv` es un **ejemplo** de parseo
(Mean ~24 V), no una bitácora firmada. Sobre DC el THDi de armónicos **no
cuenta**.

---

*Andres Barbudo Rodriguez — CFT Paillaco*

---

# 6. SIL del banco y aproximación 24 V en pañol

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

Este TPA es **24 V**, no 48 V ni 400 V. La wanptek KPS305D topea a 30 V:
por eso no se modela 48 V. No se construyó un inversor.

## Tres capas, sin mezclarlas

```text
Capa A  Software SIL     →  24 V / 120 W SIMULADOS  (power_stage/)
Capa B  Banco físico TPA →  24 VDC, wanptek KPS305D + Gratten GA1102CAL
Capa C  Fuera de TPA     →  48 V, MCU/PWM/puente, 400 V / 500 kW / ~700 A
```

Capa A: `physical_outputs_available = false` siempre. PWM y contactores
en la UI son booleanos. El PC no conmuta la fuente.

Capa B: punto 24,0 V, Ilim (demo 0,50 A) **antes** de subir V. Corte =
switch I/O. Segunda persona **clase A** si hay 24 V vivos (criterio A5:
procedimiento, no pytest).

## FSM

```text
POWER_OFF → SELF_TEST → PRECHARGE → READY → RUN
```

Precarga ≥ 90 % de Vdc **del modelo** antes del contactor lógico. E-stop
y OVERCURRENT enclavan; no hay rearranque automático (`reset_fault`
manual; si hay E-stop, primero `release_estop`). `enable` antes de READY
se rechaza. Shutdown y E-stop dejan main, precharge, gate_enable y pwm
en false.

La matriz `docs/MATRIZ_SIL_TPA.md` traza A1–A4 a
`tests/test_power_stage.py`. A5 no es un assert.

## Pañol (capacidad)

Procedimiento: `docs/PROCEDIMIENTO_SCOPE_24V.md`. CH1 Mean ≈ display de
la KPS305D. CSV USB, mapeo CH1 → va. Frase: el CSV demuestra la cadena
de archivos, no H3. Campaña firmada: **pendiente** (bitácora vacía).

---

*Andres Barbudo Rodriguez — CFT Paillaco*

---

# 7. Evidencias, límites y conclusiones

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

## Cinco logros medibles

1. DSP sobre patrón: `tests/test_dsp.py` pasa con tolerancia 12 %.
2. TAN small en el repo: 80 A, Icw 16 kA, XL³ 160, forma 2b, PDF/HTML.
3. SIL 24 V: FSM, latch, `physical_outputs_available = false` en RUN.
4. Tres vistas con `python hil_app.py`, sin Docker; suite
   `pytest tests tan_telecom/tests` en `output/tpa/pytest.txt`.
5. Alcance congelado a 24 VDC con inventario real (KPS305D + GA1102CAL)
   y procedimiento de pañol escrito.

## Cinco límites

1. No hay medición certificada ni THDi SEC.
2. No hay PWM/GPIO reales; el edge solo supervisa.
3. Python no es hard real-time.
4. No hay tablero TAN construido ni ensayo a 400 V / 48 V / ~700 A.
5. La campaña CSV de pañol firmada por clase A está pendiente.

## Tres trabajos futuros, fuera de este TPA

1. MCU/PWM sobre **24 V** si aparece hardware de laboratorio, sin
   fingir un módulo de 400 V.
2. Campaña con analizador certificado arrendado (IEC 61000-4-7), no con
   el Gratten.
3. Un TPA **nuevo** si alguna vez hay medio de prueba de barra 400/230 V.
   El siguiente paso **no** es 500 kW en el CFT Paillaco.

La hipótesis del capítulo 1 se sostiene en software: el DSP sigue al
patrón y la FSM no rearma sola. Lo que falta para el acta de laboratorio
es la fila firmada de la bitácora, no un banco de 400 V.

---

*Andres Barbudo Rodriguez — CFT Paillaco*

---

# 8. Anexos

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

| Anexo | Ruta |
|---|---|
| Alcance congelado | `docs/ALCANCE_TPA_CFT_PAILLACO.md` |
| Inventario de pañol | `docs/INVENTARIO_PANOL_CFT_PAILLACO.md` |
| Bitácora de laboratorio | `docs/BITACORA_LABORATORIO_TPA.md` |
| Matriz SIL | `docs/MATRIZ_SIL_TPA.md` |
| Informe de evidencias | `docs/INFORME_EVIDENCIAS_TPA.md` |
| Casos de demo | `docs/CASOS_DEMO_DEFENSA.md` |
| Procedimiento / protocolo 24 V | `docs/PROCEDIMIENTO_SCOPE_24V.md`, `docs/PROTOCOLO_SEGURIDAD_24V.md` |
| Carta Gantt | `docs/CARTA_GANTT_TPA.pdf` |
| Banco de preguntas | `docs/memoria/PREGUNTAS_DEFENSA.md` |
| Guion demo live | `docs/DEMO_LIVE_EXAMEN.md` |
| Índice `output/tpa/` | `output/tpa/README.md` |

## Trabajo futuro, fuera de este TPA

Ruta de producto (`docs/PRODUCT_ROADMAP_CHILE.md`): módulo 50–100 A /
400/230 VAC, MCU/PWM, 48 V si aparece fuente. **No es objetivo ni
ensayo de esta memoria.**

---

*Andres Barbudo Rodriguez — CFT Paillaco*
