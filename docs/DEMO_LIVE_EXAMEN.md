# Guion demo live — examen de título

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  

Instrumentos (no sustituir): wanptek **KPS305D** 0–30 V / 0–5 A;
Gratten **GA1102CAL** 100 MHz, 1 GSa/s, 2 canales, USB Host, PRINT.
Este software **no** energiza la fuente. `physical_outputs_available = false`.

Andres elige sede **el día anterior**.

| Sede | Dónde | Energía |
|---|---|---|
| **A** | Pañol o sala con 230 VAC de pared y mesa | KPS305D en I. **Clase A presente.** CASO D completo. |
| **B** | Aula sin banco | **No se energiza.** Placas (fotos), BMP/PRINT, CSV previo si hay. DSP = CASO A. Frase de arranque: “hoy no hay 24 V vivos”. |

---

## 1. Checklist de la noche anterior (12)

1. `python hil_app.py` arranca en el laptop de defensa.  
2. Pendrive FAT32 probado en el Gratten.  
3. Ilim preset **0,50 A**, V preset **24,0 V**, switch KPS305D en **O**.  
4. Carga resistiva P < 120 W (valor anotado; no fotografiada de fábrica).  
5. Punta CH1 (1x/10x: el que haya; si 10x, menú Probe = 10x).  
6. Clase A confirmada **solo si sede A**.  
7. Fotos de placa KPS305D y GA1102CAL en el laptop.  
8. BMP/PRINT de respaldo si existe ensayo previo.  
9. CSV de ejemplo o previo copiado (no venderlo como H3).  
10. `docs/CASOS_DEMO_DEFENSA.md` y este guion impresos.  
11. `output/tpa/` con pytest y PDF TAN small.  
12. Frase memorizada: cadena fuente–scope–CSV, no H3, no red del CFT, no 48 V.

---

## 2. Ajustes de fábrica del día

| Equipo | Ajuste |
|---|---|
| KPS305D | Ilim **0,50 A PRIMERO** · V **24,0 V** · switch **O** · LED C.V. esperado con carga liviana |
| Gratten | CH1 ON, CH2 OFF · DC · 5 V/div · Probe 1x o 10x · 5 ms/div · Trigger AUTO · MEASURE Mean, Vmax, Vmin · USB **antes** de SAVE |
| Laptop | `python hil_app.py` → Monitor AHF en patrón sintético · carpeta lista para el CSV |

---

## 3. Guion (~20 min)

| Tiempo | Qué |
|---|---|
| 0:00–1:00 | Portada. Alcance: 400 V fuera. Autor: Andres Barbudo Rodriguez, CFT Paillaco. |
| 1:00–8:00 | CASOS A–C software (Monitor, TAN, SIL). **Sin energía.** |
| 8:00–13:00 | CASO D live (sede A) o fotos (sede B). |
| 13:00–15:00 | Límites y cierre. |
| 15:00– | Preguntas (`docs/memoria/PREGUNTAS_DEFENSA.md`). |

### Tramo 8:00–13:00 — dos columnas

**Sede A (24 V vivos, clase A a la vista)**

| Paso | Andres dice | Andres hace |
|---|---|---|
| a | “KPS305D 0–30 V 0–5 A. GA1102CAL 100 MHz, 2 canales.” | Mostrar placas. |
| b | “Punto 24,0 V. Esta fuente no llega a 48 V.” | Señalar techo 30 V en la placa. |
| c | “Clase A presente. Ilim 0,50 A primero, después 24,0 V.” | Ilim, V, switch **I**. |
| d | “Display ≈ 24 V, LED C.V. Mean del Gratten ≈ 24 V.” | MEASURE Mean. |
| e | (Opcional) “Bajo Ilim y veo C.C.: así se limita corriente.” | Bajar Ilim ~20 s; volver a 0,50 A / C.V. **No** cortocircuitar. |
| f | “SAVE CSV al USB e importo CH1 como va, no como ia.” | SAVE/RECALL CSV · import Monitor. |
| g | **Obligatoria:** “Esto demuestra la cadena fuente–scope–CSV–software. No demuestra H3 ni la red del CFT.” | Señalar Mean, no el THDi. |
| h | “Corto. Cero volt en fuente y en el Gratten.” | Switch **O**. Comprobar 0 V. |

**Sede B:** no hay switch I. Fotos de placa + BMP Mean + CASO A. Primera frase: “hoy no hay 24 V vivos”.

---

## 4. Qué NO decir

| # | Prohibido |
|---|---|
| 1 | “Medimos armónicos” / “medimos la red del CFT” |
| 2 | “El AHF está compensando” |
| 3 | “48 V reales” |
| 4 | “El Gratten es clase A de medición / analizador” |
| 5 | “Python es tiempo real” |
| 6 | “Este THDi sirve para la SEC” |
| 7 | “El software energiza la fuente” |
| 8 | “Este tablero TAN está construido” |
| 9 | “Ensayamos a 400 V” |
| 10 | “La clase A sustituye el banco de 700 A” |

---

## 5. Fallos y frase de recuperación

| Fallo | Andres dice |
|---|---|
| Pendrive / CSV no abre | “USB falló. Dejo el BMP/PRINT y el DSP sigue en el patrón sintético.” |
| Probe 10x y traza ~2,4 V | “Atenuación: corrijo CH1 Probe a 10x.” |
| LED C.C. al energizar | “Ilim menor que la carga; subo Ilim o alivio. No es un AHF en falla.” |
| `hil_app.py` caído | “Muestro pytest y una captura previa. No improviso GPIO.” |
| Comisión pide 400 V | “Alcance congelado: este CFT no tiene ese medio de prueba.” |

---

## 6. Fotos mínimas (sin selfies)

Placa KPS305D · placa GA1102CAL · display 24,0 V C.V. · pantalla Gratten con Mean · dashboard con CSV importado (CH1 → va) · bitácora firmada si hubo campaña.

No hay generador de funciones ni segunda fuente en este guion.

---

*Andres Barbudo Rodriguez — CFT Paillaco — 23-ago-2026*
