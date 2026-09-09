# Banco 24 VDC — paquete TPA (tres capas)

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  
**Enmienda:** 21-ago-2026 — el TPA no prepara 48 V.

Este documento es el entregable de diseño del banco. **El repositorio no
energiza ni controla la fuente.** Inventario de campo:
`docs/INVENTARIO_PANOL_CFT_PAILLACO.md`. HIL:
`docs/POWER_STAGE_24V.md`. API: `GET /api/bench/package`.

Las tres capas no se mezclan. Misma tensión (24 V) no significa mismo
objeto: el software no es la KPS305D, y la KPS305D no es un puente.

```text
Capa A  Software SIL     →  24 V / 120 W SIMULADOS  (power_stage/)
Capa B  Banco físico TPA →  24 VDC, wanptek KPS305D + Gratten GA1102CAL
Capa C  Fuera de TPA     →  48 V, MCU/PWM/puente, 400 V.
```

---

## Capa A — Software SIL (24 V / 120 W simulados)

Máquina de estados en `power_stage/controller.py`. Límites iguales a la
placa de la KPS305D, **sin cable a la fuente**:

| Parámetro | Valor | Nota |
|---|---:|---|
| DC-link nominal | 24 V | Punto de trabajo TPA |
| Corriente | 5 A | Placa 0–5 A |
| Potencia | 120 W | 24 V × 5 A |
| Techo de fuente | 30 V | Placa KPS305D |
| Trip OV | 29 V | Dentro del techo 30 V |

`physical_outputs_available = false` **siempre**. No hay GPIO, PWM real,
drivers de compuerta ni mando de contactores. Los indicadores de PWM y
contactor en la vista Banco 24 V son booleanos del modelo.

Secuencia: `POWER_OFF → SELF_TEST → PRECHARGE → READY → RUN`.
E-stop y fallas enclavan; no hay rearranque automático.

La precarga ≥ 90 % de Vdc (A3) es del **modelo HIL**. En el pañol no hay
DC-link ni contactor principal.

---

## Capa B — Banco físico TPA (la misma 24 VDC)

Instrumentos fotografiados el 21-ago-2026, Pañol CFT Paillaco:

- **wanptek KPS305D**, 0–30 V / 0–5 A, punto 24,0 V, Ilim (demo 0,50 A).
- **Gratten GA1102CAL**, 100 MHz, 2 canales, 1 GSa/s, USB CSV/BMP.

Fuente #2, sondas, carga, E-stop de seta y generador de funciones:
**NO FOTOGRAFIADOS**. No se inventan. El corte del ensayo live es el
interruptor I/O de la KPS305D + Ilim en C.C.

Sin MOSFET de 400 V. Sin 500 kW. Sin 48 V (la KPS305D topea a 30 V).

### Unifilar (solo capa B)

```text
[KPS305D 24,0 V  Ilim 0,50 A  C.V.] — switch I/O = corte
        |
[carga resistiva de pañol, P < 120 W, I < Ilim]
        |
[CH1 Gratten GA1102CAL en bornes ±, ref. en −]
        |
[pendrive USB → CSV Time,CH1 → Monitor AHF, CH1 → va]
```

El software SIL corre en el laptop **en paralelo** y no está cableado a
la KPS305D. Un DC ~24 V prueba la cadena de archivos, no H3/H5/H7.

### Material

| Ítem | Clasificación |
|---|---|
| wanptek KPS305D, 0–30 V / 0–5 A, punto 24,0 V, Ilim | USABLE EN TPA |
| Gratten GA1102CAL, 100 MHz, 2 ch, 1 GSa/s, USB CSV/BMP | USABLE EN TPA |
| Segunda persona licencia clase A | USABLE EN TPA (A5) |
| Fuente #2, sondas, carga, E-stop de seta, generador | NO FOTOGRAFIADO |

### Riesgos

| ID | Peligro | Mitigación |
|---|---|---|
| R1 | Energizar la KPS305D sin Ilim ni clase A | Ilim 0,50 A **antes** de subir V; switch en O; clase A presente |
| R2 | Rearme automático (eso es capa A) | Falla enclavada en SIL; reset manual. El PC no rearma la fuente. |
| R3 | Creer que el laptop corta la KPS305D | `physical_outputs_available = false`. Corte = switch I/O. |
| R4 | Contacto con 24 V vivos | 0 V en display y en el Gratten, pantalla, clase A |

### Procedimiento de pañol

1. Capa A en el laptop: POWER_OFF → RUN, E-stop, latch. Sin GPIO.
2. KPS305D en O. Ilim 0,50 A, **luego** V = 24,0 V.
3. Clase A presente. Carga P < 120 W. CH1 en bornes ±.
4. Switch I. LED C.V. Display ≈ Mean del Gratten.
5. SAVE CSV USB. Import Monitor AHF, mapear CH1 → va (no ia).
6. Switch O. Comprobar 0 V en fuente y en el Gratten.
7. Declarar: el CSV no demuestra H3; el DSP se defiende con patrón sintético.

---

## Capa C — Fuera de este TPA

48 V, MCU/PWM/puente y 400 V (también 500 kW y ~700 A) quedan fuera:
no hay medio de prueba en este CFT y la KPS305D topea a 30 V.

---

## Criterios de aceptación (A1–A5)

| ID | Criterio | Capa | Cómo se demuestra |
|---|---|---|---|
| **A1** | `physical_outputs_available = false` | A | `power_stage/controller.py`, API, tests |
| **A2** | E-stop y sobrecorriente enclavados; sin rearranque automático | A | FSM y tests de `power_stage` |
| **A3** | Precarga ≥ 90 % de Vdc antes del contactor principal | A | Modelo HIL 24 V; no hay DC-link físico |
| **A4** | DSP validado con señales patrón; THDi del dashboard no es SEC | A (DSP) | `tests/test_dsp.py`; Monitor AHF |
| **A5** | Pruebas energizadas con pantalla, descarga y clase A | B | Procedimiento de pañol, no un `assert` |

La vista Banco 24 V muestra la capa A (SIL) arriba y la capa B (pañol)
abajo. No documenta un puente de 400 V ni un banco de 48 V.

---

*Andres Barbudo Rodriguez — CFT Paillaco — 21-ago-2026*
