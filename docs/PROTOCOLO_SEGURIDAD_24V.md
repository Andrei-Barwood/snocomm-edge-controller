# Protocolo de seguridad 24 VDC — TPA CFT Paillaco

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

**Prohibido en la primera línea de este protocolo:** 380/400 VAC, 500 kW
y ~700 A. **Prohibido 48 V:** la wanptek KPS305D topea a 30 V. Este
documento no es un ensayo SEC ni IEC 61000. Alcance: **solo 24 VDC**
con la wanptek KPS305D y el Gratten GA1102CAL.

---

## Segunda persona competente

| Campo | Valor |
|---|---|
| Rol | Profesional autorizado, licencia **clase A** |
| Nombre | ________________________________ |
| Firma | ________________________________ |
| Fecha | ________________________________ |

Obligatoria si la KPS305D está en **I**. No sustituye un banco de ~700 A
que este CFT no tiene.

---

## Lista pre-energía (máximo 10)

Marcar **antes** de pasar el switch a I.

| # | Ítem | OK |
|---|---|---|
| 1 | Clase A presente; nombre en esta hoja y en la bitácora | ☐ |
| 2 | Switch I/O de la KPS305D en **O**; display 0 V | ☐ |
| 3 | **Ilim = 0,50 A ANTES de subir V** (COARSE+FINE de A) | ☐ |
| 4 | V set = 24,0 V (aún en O) | ☐ |
| 5 | Carga P < 120 W, I < Ilim; no hay puente a red | ☐ |
| 6 | CH1 en bornes ±, referencia en −; Probe 1x/10x configurado en el Gratten | ☐ |
| 7 | No se intenta “subir a 48 V” ni poner fuentes en serie | ☐ |
| 8 | Pantalla / zona despejada; sin joyas en la mano de trabajo | ☐ |
| 9 | Pendrive FAT32 listo; laptop con `hil_app.py` **no** cableado a la fuente | ☐ |
| 10 | Corte acordado: switch I/O de la KPS305D (quién corta, ver abajo) | ☐ |

---

## Quién corta y cómo se comprueba 0 V

| Campo | Valor |
|---|---|
| Corte de energía | Interruptor **I/O** de la wanptek KPS305D. Ilim en C.C. es salvaguarda, no el corte. |
| Quién corta | Andres o la persona clase A, en voz alta: “corto”. |
| 0 V comprobado | Display de la KPS305D **y** MEASURE Mean del Gratten GA1102CAL ≈ 0 V. |
| E-stop de seta | No fotografiado. No inventar. El corte del ensayo live es el I/O. |

El computador **no** corta la fuente (`physical_outputs_available = false`).

---

## Prohibido

- Puente de la salida de la KPS305D a la red 230/400 V.
- “Subir a 48 V” (serie de fuentes, o pedir otra fuente para completar).
- Dejar la KPS305D en **I** sin vigilancia.
- Usar el Gratten GA1102CAL como analizador de red o como evidencia IEC/SEC.
- Presentar un CSV de 24 VDC como prueba de H3/H5/H7.

---

## Fotos de evidencia (sin selfies)

1. Setup de mesa (fuente, carga, scope, laptop).
2. Placa **wanptek KPS305D** (0–30 V / 0–5 A).
3. Placa **Gratten GA1102CAL** (100 MHz, 2 ch, 1 GSa/s).
4. Pantalla del scope: MEASURE Mean ≈ 24 V.
5. Dashboard Monitor AHF con el CSV importado (CH1 → va).

No selfies. No fotos de 400 V ni de un “banco 48 V”.

---

*Andres Barbudo Rodriguez — CFT Paillaco — 21-ago-2026*
