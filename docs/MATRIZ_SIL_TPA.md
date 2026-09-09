# Matriz SIL del TPA — criterio → test

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  
**Fecha:** 21-ago-2026  
**Capa:** A (software SIL 24 V / 120 W). A5 es capa B (pañol).

Fuente de criterios: `docs/BANCO_FISICO_24V.md` (A1–A5) y la FSM de
`power_stage/controller.py`. Los tests citados existen en el repo en esta
fecha. P05 añadió las filas que P04 marcó faltantes (salvo A5).

El modelo es 24 V / 5 A / 120 W (techo 30 V, OV 29 V), alineado a la
wanptek KPS305D. 48 V y 400 V están fuera de esta matriz.

---

## Tabla de trazabilidad

| ID | Enunciado | Archivo de test | Estado | El TPA SÍ puede mostrar | El TPA NO puede mostrar |
|---|---|---|---|---|---|
| **A1** | `physical_outputs_available = false` siempre | `tests/test_power_stage.py` · `test_physical_outputs_false_in_power_off_run_estop_and_fault` (POWER_OFF, RUN, ESTOP, FAULT). También `test_hil_rating_matches_kps305d_24v`. | **cubre** | El flag en POWER_OFF, RUN, ESTOP y FAULT_LATCHED | GPIO, PWM real, que el PC conmute la KPS305D |
| **A2** | E-stop y sobrecorriente enclavados, sin rearranque automático | `test_estop_immediately_forces_safe_outputs_and_latches`; `test_no_automatic_restart_after_overcurrent` (`start`/`enable` fallan hasta `reset_fault`) | **cubre** | Latch de E-stop lógico; OVERCURRENT enclavado; rearranque solo manual | E-stop de seta (no fotografiado); corte físico de la KPS305D |
| **A3** | Precarga ≥ 90 % de Vdc antes del contactor principal | `test_precharge_reaches_90_percent_before_ready`; timeout en `test_precharge_timeout_latches_fault` | **cubre** | `dc_bus_v ≥ 0,90 · source_v` al cerrar el contactor lógico y en READY | DC-link físico, contactor real, puente MOSFET |
| **A4** | DSP validado con señales patrón; THDi del dashboard no es SEC | `tests/test_dsp.py`: `test_h3_extracted_from_zero_sequence`, `test_h5_negative_sequence_extracted`, `test_h7_positive_sequence_extracted`, `test_thdi_uses_fundamental_not_total_rms`, `test_pll_locks_to_voltage_not_current`. `REL_TOL = 0.12`. | **cubre** | H3/H5/H7 y THDi = Ih/I1 sobre patrón a 12.8 kHz; leyenda del Monitor «Académico · no IEC/SEC» | Ensayo IEC 61000-4-7, medición SEC, THDi de un CSV de 24 VDC del Gratten |
| **A5** | Pruebas energizadas con pantalla, descarga y segunda persona clase A | No es pytest. Procedimiento en `docs/BANCO_FISICO_24V.md` (capa B) e inventario. | **no cubre** (no aplica assert) | Protocolo de pañol 24 V; bitácora el día del lab | Un test verde que sustituya a la clase A |
| **SIL-PWM** | PWM no habilita antes de READY | `test_pwm_cannot_start_before_ready` (`enable` en POWER_OFF y tras `start`, antes de READY) | **cubre** | Rechazo de `enable` fuera de READY | PWM de hardware |
| **SIL-TMO** | Timeout de precarga enclava | `test_precharge_timeout_latches_fault` | **cubre** | FAULT_LATCHED + `PRECHARGE_TIMEOUT` y salidas lógicas en false | Un DC-link que no carga en el pañol (no hay) |
| **SIL-SD** | Shutdown deja todas las salidas en false | `test_complete_safe_startup_and_shutdown` (main, precharge, gate_enable, pwm) | **cubre** | Las cuatro salidas lógicas en false tras `shutdown` | Apertura de un contactor físico |
| **SIL-ESTOP-SW** | El computador no puede anular el E-stop | `test_estop_immediately_forces_safe_outputs_and_latches`: `reset_fault` falla con «Libere» mientras el E-stop está activo | **cubre** | Latch lógico: hay que `release_estop` y luego `reset_fault` | Anular el switch I/O de la KPS305D (el PC no lo manda); E-stop de seta (no fotografiado) |
| **SIL-OV/OT** | `inject_fault` de DC_OVERVOLTAGE y OVERTEMPERATURE enclava | `test_inject_dc_overvoltage_and_overtemperature_latch` | **cubre** | FAULT_LATCHED, salidas lógicas en false, sin rearranque hasta reset | Ensayo térmico o de sobretensión reales a 24 V como evidencia de producto |

---

## Lectura de A1–A5 (sin overclaim)

- **A1** cubre en POWER_OFF, RUN, ESTOP y FAULT. Sigue siendo un booleano de software.
- **A2** cubre: E-stop enclavado y OVERCURRENT sin rearranque automático.
- **A3** cubre el 90 % en el modelo HIL. No hay DC-link físico.
- **A4** cubre. El “THDi no es SEC” es declaración de alcance y de UI, no un certificado.
- **A5** sigue siendo procedimiento de pañol (wanptek KPS305D + Gratten GA1102CAL, clase A presente). No es pytest.

---

## Tests añadidos en P05

| Función | Cierra |
|---|---|
| `test_physical_outputs_false_in_power_off_run_estop_and_fault` | A1 |
| `test_no_automatic_restart_after_overcurrent` | A2 |
| `test_precharge_reaches_90_percent_before_ready` | A3 |
| `test_inject_dc_overvoltage_and_overtemperature_latch` | SIL-OV/OT |

No se tocó el controlador: los criterios ya eran ciertos en software.
A5 no lleva función de test.

---

*Andres Barbudo Rodriguez — CFT Paillaco — 21-ago-2026*
