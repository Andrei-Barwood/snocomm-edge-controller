# Informe de evidencias del TPA

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  
**Carrera:** Electricidad  
**Repositorio:** `snocomm-edge-controller`  
**Fecha:** 23-ago-2026  
**Alcance:** `docs/ALCANCE_TPA_CFT_PAILLACO.md`

Este informe es el cuerpo de evidencias para la memoria. No es un ensayo
SEC, no es un certificado IEC y no es un ensayo a 400 V. La plataforma
**calcula y simula**. El banco físico del TPA es 24 VDC (wanptek KPS305D +
Gratten GA1102CAL). El HIL es 24 V / 120 W, `physical_outputs_available =
false`.

No se inventan resultados de laboratorio. La bitácora
(`docs/BITACORA_LABORATORIO_TPA.md`) tiene tres filas de pañol **vacías**.
La campaña física 24 V está **pendiente**. Lo que sí está cerrado es
software: pytest, DSP sobre patrón, TAN small, SIL.

---

## 1. Identificación

| Campo | Valor |
|---|---|
| Autor (único) | Andres Barbudo Rodriguez |
| Institución | CFT Paillaco |
| Tipo | Trabajo Práctico Aplicado (TPA) |
| Título de trabajo | Controlador de borde para el estudio de un filtro activo de armónicos (AHF): cálculo TAN, DSP 3P+N y SIL 24 V |
| Año | 2026 |
| Defensa de software | `python hil_app.py` y `pytest tests tan_telecom/tests` |

Un solo autor. Nada más en esa línea.

El problema que se aproxima: en tableros BT que alimentan nodos telecom,
H3 (secuencia cero) se suma en el neutro; H5 es negativa y H7 positiva.
Este TPA **no construye el AHF**. Entrega tres capas que caben en el CFT:
cálculo IEC 61439 (TAN-Telecom), DSP sobre señales patrón, y lógica segura
de un banco simulado a 24 V más un procedimiento de pañol a 24 VDC.

---

## 2. Método

La cadena de prueba es esta, y no otra:

```text
señal patrón (dsp/patterns.py)
        →  DSP auditable (Clarke αβ0, SRF-PLL, H3/H5/H7, THDi = Ih/I1)
        →  cálculo de tablero (tan_telecom, IEC 61439)
        →  lógica segura SIL (power_stage/, sin GPIO)
        →  (capacidad) CSV de osciloscopio → Monitor AHF, CH1 → va
```

Tres vistas de operador (`hil_app.py`):

| Vista | Método | Qué no es |
|---|---|---|
| Monitor AHF | Patrón `combined_it` o CSV importado | Analizador certificado |
| Diseño TAN | `run_design` + Excel/PDF | Tablero construido |
| Banco 24 V | FSM HIL 24 V / 120 W | Fuente energizada por el PC |

Comparación: contra lo que se **sabe** de la señal (patrón, o display de
la KPS305D ≈ Mean del Gratten). No contra IEC 61000 ni contra un ensayo
de tipo.

Docker, Modbus TLS e InfluxDB existen como capacidad. **No** son
requisito de defensa.

---

## 3. Evidencia DSP

Archivos: `dsp/core.py`, `dsp/patterns.py`, `tests/test_dsp.py`.  
Muestreo: 12,8 kHz, bloques de 128 muestras.  
Tolerancia declarada: `REL_TOL = 0.12` (12 % relativo).  
THDi: `100 · Ih / I1` con Ih de H3+H5+H7. No es IEC 61000-4-7.

| Test | Patrón / qué afirma |
|---|---|
| `test_clarke_ab0_roundtrip` | Transformada Clarke invertible |
| `test_zero_sequence_appears_on_neutral_and_axis_0` | Secuencia cero en eje 0 |
| `test_neutral_is_three_times_zero_sequence` | Neutro ≈ 3·I0 (H3) |
| `test_h3_extracted_from_zero_sequence` | H3 extraído, catálogo `zero_sequence_neutral` |
| `test_h5_negative_sequence_extracted` | H5, `negative_sequence_h5` |
| `test_h7_positive_sequence_extracted` | H7, `positive_sequence_h7` |
| `test_thdi_uses_fundamental_not_total_rms` | THDi = Ih/I1, no Irms/I1 |
| `test_pll_locks_to_voltage_not_current` | PLL sobre tensión del PCC |
| `test_saturation_drops_h7_first` | Saturación académica |

El patrón de demo (`config_industrial.yaml`, `combined_it`): I1 peak 100,
H3=20, H5=10, H7=5. THDi Ih/I1 esperado ≈ 22,9 % dentro del 12 %.
`tests/test_tpa_smoke.py::test_combined_it_pattern_produces_thdi` exige
THDi > 0 sobre ese patrón.

Un CSV de 24 VDC del Gratten **no** sustituye esta tabla. Sobre DC no hay
I1 senoidal; un THDi alto sería artefacto.

---

## 4. Evidencia TAN

Archivos: `tan_telecom/calculations.py`, `rules.py`, `export.py`,
`tan_telecom/tests/test_calculations.py`, `test_rules.py`.

El código **aplica** reglas de IEC 61439-1/2 a corriente, Icw/Icc,
calentamiento, forma y envolvente XL³. Eso no es “el tablero cumple IEC”.

| Test | Qué afirma |
|---|---|
| `test_corriente_nominal_base_45kw` | In base del caso 45 kW |
| `test_compute_electrical_small` | Paquete eléctrico small |
| `test_small_prefers_2b` | Forma 2b, familia TT-S |
| `test_medium_prefers_3b` | Forma 3b/4b en medium |
| `test_export_artifacts` | Excel, PDF, HTML, JSON, MD, CSV |

Artefacto de entrega (prediseño, no obra):

- `output/tpa/tan_small/TT-S-20260821-154807_resumen.pdf`
- mismo caso: `_informe.html`, `_documentacion.xlsx`
- regenerable: `python -m tan_telecom --example small --output ./output/tpa/demo_defensa -v`

Números de ese small: In selección **80 A**, Icc/Icw **16,0 kA**, ΔT
**10,7 °C**, XL³ **160** IP55, forma **2b**, 45 kW / 4 racks. La fórmula
usa 400 V como tensión de **cálculo**. No hubo ensayo a 400 V.

---

## 5. Evidencia SIL

Archivos: `power_stage/controller.py`, `tests/test_power_stage.py`,
`docs/MATRIZ_SIL_TPA.md`, `docs/POWER_STAGE_24V.md`.

Límites del modelo = placa KPS305D: 24 V, 5 A, 120 W, techo 30 V, OV 29 V.

| Criterio | Estado | Test |
|---|---|---|
| A1 `physical_outputs_available = false` | cubre | `test_physical_outputs_false_in_power_off_run_estop_and_fault` |
| A2 E-stop y OC enclavados, sin rearranque | cubre | `test_estop_…`; `test_no_automatic_restart_after_overcurrent` |
| A3 precarga ≥ 90 % de Vdc (modelo) | cubre | `test_precharge_reaches_90_percent_before_ready` |
| A4 DSP patrón; THDi no SEC | cubre | `tests/test_dsp.py` |
| A5 clase A en pruebas energizadas | no pytest | procedimiento de pañol |
| SIL-PWM, TMO, SD, ESTOP-SW, OV/OT | cubre | ver matriz |

`test_tpa_smoke.py::test_physical_outputs_false_in_run` exige el flag en
RUN. El computador no manda la KPS305D.

---

## 6. Evidencia de pañol 24 V

**Estado: pendiente de campaña.** Las filas 1–3 de
`docs/BITACORA_LABORATORIO_TPA.md` están vacías. No hay CSV real del
Gratten firmado por clase A.

Lo que **sí** existe (capacidad, no ensayo ejecutado):

| Pieza | Archivo |
|---|---|
| Inventario fotografiado 21-ago-2026 | `docs/INVENTARIO_PANOL_CFT_PAILLACO.md` |
| Procedimiento de captura | `docs/PROCEDIMIENTO_SCOPE_24V.md` |
| Protocolo (400 V prohibido en 1.ª página) | `docs/PROTOCOLO_SEGURIDAD_24V.md` |
| Bitácora (plantilla) | `docs/BITACORA_LABORATORIO_TPA.md` |
| CSV de **ejemplo** (no campaña) | `acquisition/panol_24v_gratten_example.csv` |
| Parser del ejemplo | `tests/test_acquisition.py::test_parse_panol_24v_gratten_csv` |

El ejemplo de CSV es un DC ~24 V, `Time,CH1`, cabecera estilo Gratten.
El test comprueba el parseo y que el alias por defecto de `ch1` es `ia`
(hay que mapear **CH1 → va**). Mean del ejemplo ∈ [23,5 ; 24,5] V. Eso
demuestra la cadena de archivos, **no** H3/H5/H7.

Cuando haya campaña: Ilim 0,50 A **antes** de V; clase A presente;
Mean del Gratten vs display de la KPS305D; switch O y 0 V comprobado.
Hasta entonces, H3 se defiende con `dsp/patterns.py`.

---

## 7. Límites declarados

1. Este software no mide con instrumento certificado ni inyecta corriente.
2. El THDi del dashboard es Ih/I1 de H3+H5+H7. No es IEC 61000-4-7 ni SEC.
3. Un CSV de 24 VDC del Gratten GA1102CAL no prueba espectro armónico.
4. Python sobre SO general no es hard real-time.
5. `physical_outputs_available` es false: no hay PWM, GPIO ni contactores
   mandados por este repositorio.
6. El HIL es 24 V / 120 W simulados. La KPS305D topea a 30 V: no hay 48 V.
7. No hay ensayo a 380/400 VAC, 500 kW ni ~700 A. No hay medio de prueba.
8. TAN-Telecom es prediseño. No hay tablero construido ni certificado
   IEC 61439.
9. IEC 62477-1, ISO 13850 y el RIC, si se citan, son referencia de
   diseño, no certificados obtenidos.
10. La licencia clase A del asistente no reemplaza el banco de ~700 A
    que este CFT no tiene.

---

## 8. Trazabilidad requisito → archivo → test

| Requisito | Archivo | Test o evidencia |
|---|---|---|
| Alcance congelado, 24 V, no 400 V | `docs/ALCANCE_TPA_CFT_PAILLACO.md` | documento de defensa |
| DSP H3/H5/H7, THDi Ih/I1, 12 % | `dsp/core.py`, `dsp/patterns.py` | `tests/test_dsp.py` |
| Prediseño IEC 61439 | `tan_telecom/calculations.py`, `rules.py` | `tan_telecom/tests/` |
| Import CSV/JSON | `acquisition/parser.py` | `tests/test_acquisition.py` |
| SIL A1–A4, FSM, latch | `power_stage/controller.py` | `tests/test_power_stage.py` |
| Paquete banco 24 V | `bench_package.py`, `docs/BANCO_FISICO_24V.md` | `tests/test_api.py` |
| Tres vistas | `hil_app.py`, `templates/index.html` | `tests/test_tpa_smoke.py` |
| Proyecto común | `project_store.py` | `tests/test_project_store.py` |
| Camino de defensa | suite completa | `output/tpa/pytest.txt` |
| A5 clase A | procedimiento + bitácora | **no** pytest |

Suite archivada: `pytest tests tan_telecom/tests -q` → ver
`output/tpa/pytest.txt`. Receta: `docs/EVIDENCIAS_TPA.md` §1.

---

## Afirmación / se puede decir / está prohibido decir

| Afirmación | Se puede decir | Está prohibido decir |
|---|---|---|
| El DSP sigue al patrón `combined_it` dentro de 12 % | Sí, con `tests/test_dsp.py` | “Medimos la red del CFT” |
| El THDi del Monitor es Ih/I1 de H3+H5+H7 | Sí, académico | “Este THDi vale para la SEC” |
| TAN small da 80 A, Icw 16 kA, XL³ 160 | Sí, prediseño | “Este tablero está construido / certificado” |
| El 400 V de la fórmula TAN es cálculo | Sí | “Ensayamos a 400 V en el pañol” |
| `physical_outputs_available` es false en RUN | Sí, pytest | “El PC genera el PWM / cierra contactores” |
| HIL 24 V / 120 W, techo 30 V | Sí | “Hay 48 V” / “el software energiza la KPS305D” |
| Procedimiento de pañol 24 V listo | Sí, capacidad | “Ya corrimos la campaña firmada” (bitácora vacía) |
| CSV ejemplo ~24 V se parsea | Sí, cadena de archivos | “Ese CSV prueba H3” |
| Python no es hard real-time | Sí | “Es tiempo real industrial” |
| Clase A es requisito de A5 | Sí | “La clase A sustituye el banco de 700 A” |

Casos de mesa: `docs/CASOS_DEMO_DEFENSA.md` (A Monitor, B TAN, C Banco SIL).

---

*Andres Barbudo Rodriguez — CFT Paillaco — 23-ago-2026*
