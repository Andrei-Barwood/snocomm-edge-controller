# Inventario del pañol usable en este TPA

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  
**Carrera:** Electricidad  
**Fecha de campo:** 21-ago-2026 (fotos de placa)  
**Alcance:** `docs/ALCANCE_TPA_CFT_PAILLACO.md`

Este inventario es material **fotografiado o declarado ausente**. No es un
catálogo. No se sustituye un modelo por otro “mejor”. Si aparece un aparato
nuevo, se añade una fila; el TPA sigue en 24 VDC.

---

## 1. Clasificación

| Código | Significado |
|---|---|
| **USABLE EN TPA** | Fotografiado (o persona competente) y previsto en el ensayo de 24 V. |
| **SOLO APOYO** | Hace falta para la cadena de archivos o la defensa, no es instrumento de medida. |
| **NO USAR EN TPA** | Cualquier combinación hacia 48 V, 380/400 V, 500 kW o ~700 A. |
| **NO FOTOGRAFIADO** | No aparece en el lote del 21-ago-2026. No se inventa marca ni modelo. |

---

## 2. Tabla de ítems

| Ítem | Marca / modelo | Datos de placa o estado | Clasificación |
|---|---|---|---|
| Fuente de banco #1 | wanptek KPS305D | DC POWER SUPPLY 0–30 V / 0–5 A | **USABLE EN TPA** |
| Fuente de banco #2 | — | No aparece en las fotos de este lote | **NO FOTOGRAFIADO** |
| Osciloscopio | Gratten GA1102CAL | GRATTEN · USB · 100 MHz · 1 GSa/s · DSO | **USABLE EN TPA** |
| Sondas | — | No aparecen. No afirmar diferencial ni de corriente | **NO FOTOGRAFIADO** |
| Carga resistiva / lámpara / reóstato | — | No fotografiada. No inventar ohmios | **NO FOTOGRAFIADO** |
| Contactores, E-stop de seta, bornes, fusibles DC | — | No fotografiados | **NO FOTOGRAFIADO** |
| Generador de funciones | — | No fotografiado. H3/H5/H7 = `dsp/patterns.py` | **NO FOTOGRAFIADO** |
| Pendrive USB (CSV/BMP) | — | Soporte del Gratten; FAT32 recomendado | **SOLO APOYO** |
| Laptop + `hil_app.py` | — | Importa CSV; no energiza la fuente | **SOLO APOYO** |
| Segunda persona competente | licencia clase A | Presente si hay 24 V energizados (A5) | **USABLE EN TPA** |
| Banco 48 V, 380/400 VAC, 500 kW, ~700 A | — | Fuera de medio de prueba de este CFT | **NO USAR EN TPA** |

---

## 3. Fuente de banco (única fotografiada)

| Campo | Valor de campo |
|---|---|
| Marca / modelo | wanptek KPS305D |
| Placa | DC POWER SUPPLY · 0–30 V · 0–5 A |
| Tensión de placa | 0–30 VDC, ajuste COARSE + FINE |
| Punto de trabajo TPA | **24,0 V** |
| Corriente máxima (placa) | 0–5 A, ajuste COARSE + FINE |
| Modos | C.V. (tensión constante) y C.C. (corriente limitada), con LED |
| Bornes | banana negro (−) / rojo (+) |
| Limitación de corriente | **SÍ** (modo C.C.) |
| Techo físico | **30 V** → esta fuente **no puede** entregar 48 V |
| Potencia de placa | 150 W máx. (30 V × 5 A). En el punto TPA: **24 V × 5 A = 120 W** |
| Aislamiento | Salida de banco de laboratorio. **No afirmar** aislamiento de seguridad clase II ni de convertidor. **No puentear a red.** |
| Clasificación | **USABLE EN TPA** |

Ilim de demostración: **0,50 A**, puesta **antes** de subir V. Si enciende el LED C.C., la carga pide más que Ilim: es la salvaguarda, no un fallo del TPA.

Corte de energía del ensayo live: interruptor **I/O** de la KPS305D + Ilim en C.C. No hay E-stop de seta fotografiado.

### Fuente #2

No aparece en las fotos de este lote. **No se inventa** marca ni modelo.
El TPA se defiende con la KPS305D. Si aparece otra, se añade una fila
**sin cambiar el alcance** (sigue 24 V, no 48 V). Clasificación: **NO FOTOGRAFIADO**.

---

## 4. Osciloscopio (fotografiado)

| Campo | Valor de campo |
|---|---|
| Marca / modelo | Gratten GA1102CAL |
| Placa | GRATTEN · USB · GA1102CAL · 100 MHz · 1 GSa/s · DIGITAL STORAGE OSCILLOSCOPE |
| Canales | 2 (CH1, CH2) + EXT trigger |
| Ancho de banda | 100 MHz |
| Muestreo | 1 GSa/s |
| USB Host frontal | Sí (pendrive) |
| Controles usados en el TPA | PRINT, SAVE/RECALL, AUTO, RUN/STOP, SINGLE, MATH, REF, MEASURE |
| Exporta CSV | **SÍ** — CSV y bitmap **hacia** el pendrive. El CSV no se reimporta al scope. |
| Formato de export | Confirmar en el primer dump. Típico Gratten/Atten: bloque de cabecera + `Time, CH1[, CH2]`. `acquisition/parser.py` acepta `ch1` / `channel1` / `c1` y salta filas no numéricas. **No asumir 4 canales.** |
| Qué no es | No es analizador de red. No es IEC 61000. No captura 3P+N a la vez. |
| Clasificación | **USABLE EN TPA** |

---

## 5. Lo no fotografiado (no inventar)

### Sondas

No aparecen en las fotos. **No afirmar** sonda diferencial ni de corriente.

Pendiente de verificar 1x/10x pasivas el día del lab. Si hay 10x, configurar
atenuación en el Gratten (CH1 Probe). Clasificación: **NO FOTOGRAFIADO**.

### Carga resistiva o lámpara / reóstato

No fotografiada. **No inventar valor.** El unifilar mínimo cabe con
“carga resistiva de pañol, P < 120 W, I < Ilim”. El día del lab Andres
anota ohmios o lámpara real en la bitácora. Clasificación: **NO FOTOGRAFIADO**.

### Contactores, E-stop de seta, bornes, fusibles DC

No fotografiados. **No son USABLE EN TPA** mientras no estén.
El corte de energía del ensayo live es el interruptor I/O de la KPS305D
más Ilim en C.C. Clasificación: **NO FOTOGRAFIADO**.

### Generador de funciones

No fotografiado. **No inventar.** H3/H5/H7 se demuestran con
`dsp/patterns.py` (sintético). El Gratten no reemplaza al generador.
Clasificación: **NO FOTOGRAFIADO**.

---

## 6. Prohibiciones de este pañol

Queda prohibido, en cableado, procedimiento o documentación de ensayo:

1. Cualquier combinación que lleve a **380/400 VAC**, 500 kW o ~700 A.
2. Cualquier intento de “llegar a **48 V**”. La KPS305D topea a **30 V**.
   No se ponen fuentes en serie. No se busca una segunda fuente para
   “completar” 48 V. Si aparece otra fuente, el TPA **sigue en 24 V**.
3. Puentear la salida de la KPS305D a la red.
4. Afirmar aislamiento clase II o de convertidor de esta fuente.
5. Usar el Gratten como analizador certificado o como captura 3P+N.
6. Presentar un CSV de ~24 VDC como prueba de H3/H5/H7.

El modelo HIL de 48 V / 500 W, si se cita, es **solo software histórico**
(`docs/POWER_STAGE_48V.md`, retirado del alcance el 21-ago-2026).
El HIL vigente es 24 V / 120 W (`docs/POWER_STAGE_24V.md`), mismos
límites que la KPS305D.

---

## 7. Circuito mínimo de captura a 24 V

Unifilar del ensayo que sí cabe. Solo lo listado. Sin puente MOSFET. Sin 3P+N.

```text
[KPS305D 24,0 V  Ilim 0,50 A  C.V.] — switch I/O = corte
        |
[carga resistiva de pañol, P < 120 W, I < Ilim]
        |
[CH1 Gratten GA1102CAL en bornes ±, ref. en −]
        |
[pendrive USB → CSV Time,CH1 → Monitor AHF, CH1 → va]
```

Ocho líneas máximo. La KPS305D no está cableada al software HIL.

Energizar: Ilim **antes** de subir V; clase A presente; al terminar,
switch O y 0 V comprobado en el display y en el Gratten.

---

## 8. CSV que debe salir del Gratten

Para `acquisition/parser.py`:

| Campo | Qué pedir |
|---|---|
| Columnas | `Time`, `CH1` (y `CH2` solo si se usa) |
| Cabecera | Típico Gratten/Atten: bloque de texto + fila `Time,CH1`. El parser salta filas no numéricas. |
| Canales | 2. No asumir 4 columnas ni 3P+N. |
| Import en Monitor AHF | Mapear **CH1 → va** si CH1 es tensión de la fuente. |
| Alias por defecto | `ch1` / `channel1` / `c1` caen a **ia** en `acquisition/parser.py`. **No dejarlo así** en un DC de 24 V. |
| Qué demuestra un DC ~24 V | Cadena de archivos fuente → scope → CSV → software. Mean ≈ display de la KPS305D. |
| Qué **no** demuestra | H3, H5, H7 ni THDi académico útil. Sobre DC no hay I1 senoidal: el DSP de armónicos es **artefacto**. H3/H5/H7 se defienden con `dsp/patterns.py`. |

Formato de export: confirmar en el primer dump real. Hasta entonces, el
parser se prueba con un CSV corto de ejemplo, no con un dump de millones
de líneas.

---

## 9. Lo que este pañol NO permite

| Capacidad | ¿Cabe aquí? | Por qué |
|---|---|---|
| ~700 A | No | No hay banco de corriente de cortocircuito. |
| 500 kW | No | No hay carga ni fuente de esa potencia. |
| 380/400 VAC | No | No hay medio de prueba. Fuera del TPA. |
| 48 V reales | No | KPS305D topea a 30 V. No hay segunda fuente fotografiada. |
| 3P+N simultáneo | No | Gratten: 2 canales. |
| Analizador certificado / IEC 61000 / SEC | No | El GA1102CAL es DSO de 100 MHz, no analizador de red. |
| PWM / GPIO / contactores mandados por este software | No | `physical_outputs_available = false`. Corte = switch I/O. |
| H3/H5/H7 con 24 VDC | No | Un DC no tiene I1 senoidal. Patrón sintético. |

La licencia clase A habilita trabajos de BT en otro contexto. **No
reemplaza** el banco de ~700 A que este CFT no tiene.

---

## 10. Qué SÍ se demuestra en vivo en el examen

Con la wanptek KPS305D y el Gratten GA1102CAL (clase A presente si hay
24 V energizados):

1. Placas: KPS305D 0–30 V / 0–5 A y GA1102CAL 100 MHz, 2 canales, 1 GSa/s.
2. 24,0 V limitados (C.V.) y el techo 30 V (por eso el TPA no es 48 V).
3. Límite de corriente: bajar Ilim y ver LED C.C.
4. CH1 del Gratten midiendo ~24 V (MEASURE Mean) frente al display de la fuente.
5. SAVE CSV a pendrive USB → import en Monitor AHF (cadena de archivos).
6. PRINT/BMP de la pantalla del scope como evidencia.

Si la comisión está en aula sin energía, estos seis puntos pasan a fotos
de placa, BMP/PRINT y, si existe, un CSV de ensayo previo. No se energiza.

---

*Andres Barbudo Rodriguez — CFT Paillaco — 21-ago-2026*
