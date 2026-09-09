# Procedimiento de captura 24 V — Gratten GA1102CAL

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  
**Alcance:** ensayo de laboratorio del TPA. No es un AHF de 400 V ni un
ensayo SEC.

Instrumentos (fotos 21-ago-2026):

- Fuente: **wanptek KPS305D**, 0–30 V / 0–5 A, punto 24,0 V.
- Osciloscopio: **Gratten GA1102CAL**, 100 MHz, 2 canales, 1 GSa/s, USB Host.
- Generador de funciones: **NO fotografiado**. No se usa. H3/H5/H7 =
  `dsp/patterns.py` (**SINTÉTICO**).

Inventario: `docs/INVENTARIO_PANOL_CFT_PAILLACO.md`.  
Seguridad: `docs/PROTOCOLO_SEGURIDAD_24V.md`.  
Bitácora: `docs/BITACORA_LABORATORIO_TPA.md`.

---

## Cuándo CSV real y cuándo patrón sintético

| Qué se quiere demostrar | Medio | Dónde |
|---|---|---|
| Cadena fuente → scope → CSV → Monitor (Mean ≈ 24 V) | CSV real del Gratten | Este procedimiento |
| H3, H5, H7, THDi académico Ih/I1, PLL ~50 Hz | Patrón sintético | `dsp/patterns.py`, Monitor AHF sin CSV |
| THDi IEC / SEC / red del CFT | No cabe en este TPA | — |

Un DC de ~24 V **no** prueba H3/H5/H7. No hay I1 senoidal. Un THDi alto
sobre DC es **artefacto**. En el import, mapear **CH1 → va** (el alias
por defecto de `ch1` en `acquisition/parser.py` es **ia**: no dejarlo así).

---

## 1. Seguridad (antes de tocar el switch I)

Clase A presente si la KPS305D va a quedar en **I**. Corte de energía =
interruptor **I/O** de la fuente. Al terminar: switch **O** y 0 V en el
display de la KPS305D **y** en el Mean del Gratten.

Ilim **antes** de subir V. No puentear a red. No “subir a 48 V” (tope 30 V).

---

## 2. Fuente — wanptek KPS305D

1. Switch **O**. Carga resistiva de pañol, P < 120 W, I < Ilim (valor el
   día del lab; no está fotografiada).
2. **ANTES de I:** Ilim = **0,50 A** (COARSE + FINE de A).
3. Luego V = **24,0 V** (COARSE + FINE de V).
4. CH1 del Gratten en bornes ± (referencia en **−**). Probe 1x o 10x:
   pendiente de verificar el día del lab; si hay 10x, CH1 Probe = 10X.
5. Clase A presente. Switch **I**.
6. LED esperado: **C.V.** Si enciende **C.C.**, la carga pide más que
   Ilim: eso es la salvaguarda, no un fallo del TPA. Bajar V o aliviar
   carga; no subir Ilim “para que arranque”.

---

## 3. Scope — Gratten GA1102CAL

**Captura DC (ensayo TPA):**

- CH1 ON, CH2 OFF. Acoplamiento **DC**. 5 V/div. Base **5 ms/div**.
- Trigger **AUTO** (un DC no necesita flanco).
- MEASURE: **Mean**, **Vmax**, **Vmin**. Mean debe ≈ display de la KPS305D
  (24,0 V). Si Probe 10x está mal, Mean ~2,4 V: corregir CH1 Probe.

**Rizado (opcional, no es H3):**

- CH1 **AC**, 50 mV/div, 10 µs/div. Muestra el rizado de la fuente
  conmutada. No es espectro 3P+N.

Si Andres se pierde en el examen: botón **AUTO** (azul), volver a DC
5 V/div / 5 ms/div.

---

## 4. Export CSV y evidencia

1. Pendrive FAT32 en USB Host **frontal**.
2. SAVE/RECALL → tipo **CSV** → Save. El CSV sale del scope al pendrive;
   no se reimporta al Gratten.
3. BMP o **PRINT** de la pantalla (Mean ≈ 24 V) como foto de evidencia.
4. Switch **O**. Comprobar 0 V en display y en el Gratten.

Formato típico Gratten/Atten: bloque de cabecera + `Time, CH1`.
`acquisition/parser.py` salta filas no numéricas y líneas `#`. Confirmar
en el primer dump. No asumir 4 canales.

---

## 5. Import en Monitor AHF

1. En el laptop: `python hil_app.py` → http://localhost:8080 → **Monitor AHF**.
2. Importar el CSV. Mapear **CH1 → va**. No dejar el alias `ch1` → `ia`.
3. Anotar en bitácora: Mean del Gratten, display KPS305D, archivo CSV.
4. Declarar en voz alta: “esto prueba la cadena de archivos, no H3”.

H3/H5/H7 se muestran **después**, con el patrón sintético del Monitor
(`combined_it` en `config_industrial.yaml`), sin la KPS305D.

---

## 6. Señal inyectada | DSP | tolerancia

| Señal inyectada | Qué debe reportar el DSP | Tolerancia | Origen |
|---|---|---|---|
| DC 24,0 V, KPS305D, CH1 en bornes | Mean ≈ 24 V (cadena de archivos). H3/H5/H7 **no aplican**. THDi sobre DC = artefacto (N/A). | Display vs Mean: ± 0,5 V (Probe bien configurado) | **PAÑOL** |
| `combined_it` (I1=100, H3=20, H5=10, H7=5) | PLL ~50 Hz; H3, H5, H7; THDi = Ih/I1 ≈ 22,9 % | `REL_TOL = 0.12` en `tests/test_dsp.py` | **SINTÉTICO** |
| `zero_sequence_neutral` (H3=20) | H3 extraído; neutro ≈ 3·I0 | 12 % relativo | **SINTÉTICO** |
| `negative_sequence_h5` (H5=10) | H5 de secuencia negativa | 12 % relativo | **SINTÉTICO** |
| `positive_sequence_h7` (H7=5) | H7 de secuencia positiva | 12 % relativo | **SINTÉTICO** |

El pañol **no puede** inyectar H3: no hay generador de funciones
fotografiado y el Gratten tiene 2 canales (no 3P+N). Esas filas son
**SINTÉTICO**.

---

## 7. CSV mínimo compatible con `parse_csv`

Archivo de ejemplo en el repo: `acquisition/panol_24v_gratten_example.csv`.

```text
# GRATTEN GA1102CAL DIGITAL STORAGE OSCILLOSCOPE
# Coupling: DC
Time,CH1
-0.025000,24.03
0.000000,24.02
0.025000,24.02
```

Tras el import, mapear CH1 → **va**. Un Mean ~24 V no se vende como H3.

---

*Andres Barbudo Rodriguez — CFT Paillaco — 21-ago-2026*
