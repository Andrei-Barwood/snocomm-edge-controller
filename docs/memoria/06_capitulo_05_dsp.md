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
