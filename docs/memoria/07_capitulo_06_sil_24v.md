# 6. SIL del banco y aproximación 24 V en pañol

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

Este TPA es **24 V**, no 48 V ni 400 V. La wanptek KPS305D topea a 30 V:
por eso no se modela 48 V. No se construyó un inversor.

## Tres capas, sin mezclarlas

```text
Capa A  Software SIL     →  24 V / 120 W SIMULADOS  (power_stage/)
Capa B  Banco físico TPA →  24 VDC, wanptek KPS305D + Gratten GA1102CAL
Capa C  Fuera de TPA     →  48 V, MCU/PWM/puente, 400 V / 500 kW / ~700 A
```

Capa A: `physical_outputs_available = false` siempre. PWM y contactores
en la UI son booleanos. El PC no conmuta la fuente.

Capa B: punto 24,0 V, Ilim (demo 0,50 A) **antes** de subir V. Corte =
switch I/O. Segunda persona **clase A** si hay 24 V vivos (criterio A5:
procedimiento, no pytest).

## FSM

```text
POWER_OFF → SELF_TEST → PRECHARGE → READY → RUN
```

Precarga ≥ 90 % de Vdc **del modelo** antes del contactor lógico. E-stop
y OVERCURRENT enclavan; no hay rearranque automático (`reset_fault`
manual; si hay E-stop, primero `release_estop`). `enable` antes de READY
se rechaza. Shutdown y E-stop dejan main, precharge, gate_enable y pwm
en false.

La matriz `docs/MATRIZ_SIL_TPA.md` traza A1–A4 a
`tests/test_power_stage.py`. A5 no es un assert.

## Pañol (capacidad)

Procedimiento: `docs/PROCEDIMIENTO_SCOPE_24V.md`. CH1 Mean ≈ display de
la KPS305D. CSV USB, mapeo CH1 → va. Frase: el CSV demuestra la cadena
de archivos, no H3. Campaña firmada: **pendiente** (bitácora vacía).

---

*Andres Barbudo Rodriguez — CFT Paillaco*
