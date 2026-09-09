# Bitácora de laboratorio TPA

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  
**Instrumentos:** wanptek KPS305D (24,0 V, Ilim) + Gratten GA1102CAL.  
**Esto no es un ensayo SEC.** Un DC de 24 V no demuestra H3/H5/H7.

Plantilla para llenar a mano o en digital el día del lab. Tres filas
vacías = campañas físicas pendientes. La fila 4 es **SINTÉTICA** (formato,
no ensayo energizado).

Segunda persona (clase A), nombre: ________________________________

---

| Campo | Fila 1 (pañol) | Fila 2 (pañol) | Fila 3 (pañol) | Fila 4 **SINTÉTICO** |
|---|---|---|---|---|
| Fecha | | | | 21-ago-2026 (ejemplo de formato) |
| Hora | | | | — (sin 24 V vivos) |
| Asistente clase A | | | | N/A — no hay fuente energizada |
| Fuente | wanptek KPS305D | wanptek KPS305D | wanptek KPS305D | No aplica |
| Vset (V) | | | | — |
| Ilim (A) | | | | — |
| Modo C.V. / C.C. | | | | — |
| Scope | Gratten GA1102CAL | Gratten GA1102CAL | Gratten GA1102CAL | No aplica |
| V/div | | | | — |
| Acoplamiento DC/AC | | | | — |
| Probe 1x / 10x | | | | — |
| Archivo CSV | | | | `dsp/patterns.py` patrón `combined_it` (`config_industrial.yaml`) |
| fs | | | | 12 800 Hz |
| Esperado | Mean ≈ 24 V (display KPS305D) | Mean ≈ 24 V | Mean ≈ 24 V | I1 peak 100; H3=20; H5=10; H7=5; PLL ~50 Hz; THDi Ih/I1 ≈ 22,9 % |
| Salido | | | | Ver `tests/test_dsp.py` (suite del patrón) |
| THDi académico | N/A en DC | N/A en DC | N/A en DC | ≈ 22,9 % (H3+H5+H7 / I1). No es IEC/SEC |
| Desviación | | | | ≤ 12 % relativo (`REL_TOL = 0.12`) |
| Firma Andres | | | | Formato de ejemplo — no es campaña física |
| Firma clase A | | | | N/A |

Notas de la fila 4: el pañol no inyecta H3. Esa evidencia es **SINTÉTICA**.
El CSV de pañol (filas 1–3) demuestra Mean ≈ 24 V y la cadena de archivos,
con mapeo CH1 → va. No se anota un THDi de DC como resultado de armónicos.

---

*Andres Barbudo Rodriguez — CFT Paillaco — 21-ago-2026*
