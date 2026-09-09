# 7. Evidencias, límites y conclusiones

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

## Cinco logros medibles

1. DSP sobre patrón: `tests/test_dsp.py` pasa con tolerancia 12 %.
2. TAN small en el repo: 80 A, Icw 16 kA, XL³ 160, forma 2b, PDF/HTML.
3. SIL 24 V: FSM, latch, `physical_outputs_available = false` en RUN.
4. Tres vistas con `python hil_app.py`, sin Docker; suite
   `pytest tests tan_telecom/tests` en `output/tpa/pytest.txt`.
5. Alcance congelado a 24 VDC con inventario real (KPS305D + GA1102CAL)
   y procedimiento de pañol escrito.

## Cinco límites

1. No hay medición certificada ni THDi SEC.
2. No hay PWM/GPIO reales; el edge solo supervisa.
3. Python no es hard real-time.
4. No hay tablero TAN construido ni ensayo a 400 V / 48 V / ~700 A.
5. La campaña CSV de pañol firmada por clase A está pendiente.

## Tres trabajos futuros, fuera de este TPA

1. MCU/PWM sobre **24 V** si aparece hardware de laboratorio, sin
   fingir un módulo de 400 V.
2. Campaña con analizador certificado arrendado (IEC 61000-4-7), no con
   el Gratten.
3. Un TPA **nuevo** si alguna vez hay medio de prueba de barra 400/230 V.
   El siguiente paso **no** es 500 kW en el CFT Paillaco.

La hipótesis del capítulo 1 se sostiene en software: el DSP sigue al
patrón y la FSM no rearma sola. Lo que falta para el acta de laboratorio
es la fila firmada de la bitácora, no un banco de 400 V.

---

*Andres Barbudo Rodriguez — CFT Paillaco*
