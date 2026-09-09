# Banco HIL de potencia — 24 V / 120 W

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  
**Enmienda:** 21-ago-2026 — el modelo deja de ser 48 V / 500 W.

## Alcance

Esta etapa valida la lógica segura (SIL) del banco **en la misma clase de
tensión que el pañol**: 24 VDC, 5 A, 120 W. El controlador es exclusivamente
`HIL_SIMULATION_ONLY`: no contiene GPIO, PWM, drivers de compuerta ni control
de la wanptek KPS305D. `physical_outputs_available` es `false` siempre.

La fuente real es la **wanptek KPS305D** (0–30 V / 0–5 A). El HIL usa el mismo
punto de trabajo (24,0 V) y no pide 48 V: esa tensión no cabe en la placa.

48 V, 400/230 VAC, 500 kW y ~700 A están **fuera de este TPA**.

El paquete de unifilar, riesgos, material de pañol, procedimiento y criterios
de aceptación está en `docs/BANCO_FISICO_24V.md` y en `GET /api/bench/package`.

## Límites del modelo (alineados a la KPS305D)

| Parámetro | Valor HIL | Origen |
|---|---:|---|
| DC-link nominal | 24 V | Punto de trabajo TPA |
| Techo de fuente | 30 V | Placa KPS305D |
| Corriente nominal | 5,0 A | Placa KPS305D |
| Potencia | 120 W | 24 V × 5 A |
| Trip de sobrecorriente | 5,5 A | Justo sobre el rating |
| Trip de sobretensión | 29 V | Dentro del techo 30 V |
| Trip de subtensión | 18 V | 75 % de 24 V |
| Trip térmico | 85 °C | Modelo SIL |

Estos valores permiten probar software **y contrastar 24 V con el Gratten
GA1102CAL**. No son límites homologados de un producto.

## Secuencia implementada

```text
POWER_OFF → SELF_TEST → PRECHARGE → READY → RUN
```

Desde cualquier estado energizado, una falla conduce a `FAULT_LATCHED` o
`ESTOP`. Ambos estados fuerzan PWM, gate-enable y contactores lógicos a
false, con rearme manual. El switch I/O de la KPS305D es el corte físico
del ensayo de laboratorio; el computador no lo manda.

## División de responsabilidades

### Software de este TPA

- Máquina de estados y latch de fallas.
- Dashboard y API (`/api/power-stage/*`).
- Importación CSV del Gratten.
- Nunca genera PWM ni puede anular un trip ni conmutar la fuente.

### Ensayo de laboratorio (pañol)

- wanptek KPS305D a 24,0 V, Ilim puesta.
- Gratten GA1102CAL CH1, SAVE CSV USB.
- Segunda persona licencia clase A si hay 24 V energizados.

### Fuera de este TPA

- MCU/PWM/puente, 48 V, 400 V, 500 kW.

## API HIL

```text
GET  /api/power-stage/status
POST /api/power-stage/command
```

El API devuelve siempre `physical_outputs_available: false` y
`measurements.source_v = 24.0` en reposo.
