# Alcance congelado del TPA

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  
**Carrera:** Electricidad  
**Repositorio:** `snocomm-edge-controller`  
**Fecha de congelamiento:** 19-ago-2026  
**Enmienda de tensión:** 21-ago-2026 — HIL y banco físico unificados a 24 VDC (wanptek KPS305D). 48 V fuera de este TPA.

Este documento es la referencia de defensa (≈ 10 minutos). Prima sobre el README y sobre cualquier portada o roadmap de producto que mezcle este TPA con un módulo de 400 V.

---

## 1. Identificación

| Campo | Valor |
|---|---|
| Autor | Andres Barbudo Rodriguez |
| Institución | CFT Paillaco |
| Carrera | Electricidad |
| Tipo de trabajo | Trabajo Práctico Aplicado (TPA) |
| Entrega de software | Plataforma académica: calcula y simula |

Un solo autor. No hay segundo autor en este TPA.

---

## 2. Problema eléctrico que este TPA aproxima

En tableros de baja tensión que alimentan nodos de telecomunicaciones (cargas monofásicas, fuentes conmutadas, desequilibrio) aparecen armónicos de secuencia cero. El 3.º armónico (H3) no se cancela entre fases: se suma en el **neutro**. H5 es de secuencia negativa y H7 de secuencia positiva. Un filtro activo de armónicos (AHF) de cuatro ramas (3P+N) es la respuesta de producto a ese fenómeno.

Este TPA **no construye ese filtro**. Aproxima el problema en tres capas que sí caben en el CFT Paillaco:

1. **Cálculo** de tablero BT (preingeniería IEC 61439, TAN-Telecom).
2. **DSP** sobre señales patrón 3P+N: Clarke αβ0, PLL sobre tensión del PCC, extracción H3/H5/H7 y THDi académico Ih/I1.
3. **Lógica segura** de un banco de potencia **simulada a 24 V / 120 W** (máquina de estados, E-stop enclavado, sin salidas físicas) y un ensayo de laboratorio a **24 VDC** con la wanptek KPS305D y el Gratten GA1102CAL.

El fenómeno se estudia; la compensación no se inyecta a la red. No hay ensayo a 380/400 VAC, 500 kW ni ~700 A: el CFT Paillaco no dispone de ese medio de prueba.

---

## 3. Qué SÍ entrega este TPA

Cada ítem apunta al archivo o ensayo que lo demuestra. Nada de esta lista es un producto comercial ni un tablero construido.

| # | Entrega | Demostración |
|---|---|---|
| 1 | DSP 3P+N: Clarke αβ0, SRF-PLL, H3/H5/H7, THDi = Ih/I1, muestreo 12.8 kHz por microbloques | `dsp/core.py`, `dsp/patterns.py`, `tests/test_dsp.py` (tolerancia relativa 12 %) |
| 2 | Prediseño de tablero TAN-Telecom (Icw/Icc, calentamiento, envolvente XL³, forma, Excel/PDF) | `tan_telecom/` (`calculations.py`, `rules.py`, `export.py`), `tan_telecom/tests/` |
| 3 | Importación de campaña CSV/JSON de osciloscopio al Monitor AHF | `acquisition/parser.py`, `acquisition/pipeline.py`, `acquisition_service.py`, `tests/test_acquisition.py` |
| 4 | Banco SIL (HIL) 24 V / 120 W: FSM POWER_OFF → RUN, E-stop y fallas enclavadas, `physical_outputs_available = false` siempre | `power_stage/controller.py`, `tests/test_power_stage.py`, `docs/POWER_STAGE_24V.md` |
| 5 | Tres vistas de operador: Monitor AHF, Diseño TAN, Banco 24 V (SIL) | `hil_app.py`, `templates/index.html`, `static/app.js`, `tests/test_api.py` |
| 6 | Paquete documental del banco físico TPA a 24 VDC (unifilar, riesgos, A1–A5) | `docs/BANCO_FISICO_24V.md`, `bench_package.py` |
| 7 | Proyecto común (THDi observado, prediseño TAN, estado del banco) | `project_store.py`, `tests/test_project_store.py` |
| 8 | Carta Gantt y ruta de producto (esta última **no** es alcance de ensayo) | `docs/CARTA_GANTT_TPA.pdf`, `docs/PRODUCT_ROADMAP_CHILE.md` |

El software se defiende con `python hil_app.py` y `pytest`. Docker, Modbus TLS e InfluxDB son capacidad, no requisito de la defensa.

---

## 4. Qué NO entrega

Este TPA **no** entrega:

1. Ensayo, cableado, ni simulación como producto de un banco **48 V** ni **380/400 VAC**.
2. Ensayo de **500 kW** ni de **~700 A**.
3. Medición con instrumento certificado (analizador de red, laboratorio SEC).
4. Inyección de corriente de compensación a la red o a un tablero de cliente.
5. PWM, GPIO, drivers de compuerta o mando de contactores reales desde este software. El edge **solo supervisa**.
6. Hard real-time: Python sobre un SO general no lo garantiza (`README.md`).
7. Tablero TAN construido, ensayado o certificado IEC 61439.
8. Producto comercial AHF, módulo 50–100 A, ni venta.
9. Conformidad de producto (IEC 62477-1, IEC 61000, SEC). Esas normas, si se citan, son **referencia de diseño**, no certificado obtenido.
10. THDi del dashboard como evidencia IEC/SEC. Es Ih/I1 de H3+H5+H7 sobre la señal que el DSP ve.

La licencia clase A de un profesional asistente habilita trabajos de BT en otro contexto. **No reemplaza** el banco de ~700 A que este CFT no tiene.

---

## 5. Medios reales del pañol

Disponibles para este TPA (fotos 21-ago-2026):

- Fuente de banco **wanptek KPS305D**, 0–30 V / 0–5 A, punto de trabajo **24,0 V**, Ilim en modo C.C.
- Osciloscopio **Gratten GA1102CAL**, 100 MHz, 1 GSa/s, 2 canales, CSV/BMP por USB.
- Segunda persona competente: profesional autorizado con **clase A**, presente en toda prueba con 24 V energizados.

Reglas de laboratorio:

- Banco físico **y** modelo HIL del TPA = **24 VDC, corriente limitada** (5 A, 120 W).
- Pantalla, descarga comprobada y clase A presente antes de energizar.
- Prohibido puentear a red, “subir” a 48 V (la KPS305D topea a 30 V) o a 400 V.
- 48 V no es medio de prueba de este TPA. El inventario detallado va en `docs/INVENTARIO_PANOL_CFT_PAILLACO.md` cuando P02 lo genere.

---

## 6. Relación con el software (tres vistas)

| Vista | Qué es | Qué no es |
|---|---|---|
| **Monitor AHF** | DSP sobre patrón sintético o CSV importado. THDi académico. | Analizador certificado. Medición de la red del CFT. |
| **Diseño TAN** | Prediseño IEC 61439 (cálculo + expediente). | Tablero construido ni ensayado. |
| **Banco 24 V (SIL)** | Modelo HIL 24 V / 120 W **solo software**, mismos límites que la KPS305D. FSM, interlocks, API. | GPIO. No conmuta la fuente. |

Separación obligatoria de capas:

```text
Capa A  Software SIL     →  24 V / 120 W SIMULADOS  (power_stage/)
Capa B  Banco físico TPA →  24 VDC, wanptek KPS305D + Gratten GA1102CAL
Capa C  Fuera de TPA     →  48 V; MCU/PWM/puente; 400 V / 500 kW / ~700 A
```

`physical_outputs_available` es `false` siempre. Este repositorio no genera PWM ni cierra contactores.

---

## 7. Criterios de aceptación

### Banco (A1–A5)

Tomados de `docs/BANCO_FISICO_24V.md`. No se añaden normas que el código no use.

| ID | Criterio | Cómo se demuestra en este TPA |
|---|---|---|
| **A1** | `physical_outputs_available = false` en este software | `power_stage/controller.py`, snapshot de API, `tests/test_power_stage.py` |
| **A2** | E-stop y sobrecorriente enclavados; sin rearranque automático | FSM en `power_stage/controller.py` y tests asociados |
| **A3** | Precarga ≥ 90 % de Vdc antes del contactor principal | Modelo HIL 24 V (simulado); no hay DC-link físico ni puente |
| **A4** | DSP validado con señales patrón; THDi del dashboard no es evidencia SEC | `tests/test_dsp.py`; declaración en Monitor AHF |
| **A5** | Pruebas energizadas con pantalla, descarga y segunda persona **clase A** | Procedimiento de pañol 24 V, no un `assert` de pytest |

### DSP

- Patrones de `dsp/patterns.py` procesados a 12.8 kHz.
- Error relativo declarado: `REL_TOL = 0.12` en `tests/test_dsp.py`.
- THDi = 100 · Ih / I1 de las componentes H3+H5+H7 (`dsp/core.py`). No es IEC 61000-4-7 ni SEC.

### TAN

- El código aplica reglas de **IEC 61439-1/2** a corriente, Icw/Icc, calentamiento, forma y envolvente XL³ (`tan_telecom/calculations.py`, `tan_telecom/rules.py`).
- Los tests en `tan_telecom/tests/` verifican el cálculo, no un tablero de laboratorio.
- Un expediente Excel/PDF generado es prediseño, no certificación.

### Lo que no es criterio de este TPA

IEC 61000 (medición EMC), ensayo de tipo de tablero, hard real-time, y cualquier prueba a 400 V / 500 kW / ~700 A.

---

## 8. Firma de congelamiento

| Campo | Valor |
|---|---|
| Fecha | 19-ago-2026 |
| Autor | Andres Barbudo Rodriguez |
| Institución | CFT Paillaco |
| Decisión | **El alcance no se abre a 400 V sin un TPA nuevo.** |

Congelado explícitamente fuera de este TPA: **48 V**, 380/400 VAC, 500 kW, ~700 A, PWM real, inyección de corriente, medición certificada y producto comercial.

Cualquier ampliación a barra 400/230 VAC exige diseño nuevo, medio de prueba que este CFT no tiene, revisión independiente y un TPA distinto.

---

*Andres Barbudo Rodriguez — CFT Paillaco — 19-ago-2026, enmienda 21-ago-2026*
