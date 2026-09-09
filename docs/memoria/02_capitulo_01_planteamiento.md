# 1. Planteamiento y alcance

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

Este TPA nace de un problema eléctrico concreto, no de un producto que
yo pretenda vender. En tableros de baja tensión que alimentan nodos de
telecomunicaciones —racks con fuentes conmutadas, cargas monofásicas,
algo de desequilibrio— aparecen armónicos. El 3.º (H3) es de secuencia
cero: no se cancela entre fases y se **suma en el neutro**. H5 es de
secuencia negativa; H7, de secuencia positiva. Un filtro activo de
armónicos (AHF) de cuatro ramas (3P+N) es la respuesta de industria a
ese fenómeno.

En el CFT Paillaco yo no construyo ese filtro. No hay banco para ensayar
~700 A a 380/400 V ni 500 kW. La licencia clase A de un profesional
asistente habilita trabajos de BT en otro contexto; **no reemplaza** el
medio de prueba que este CFT no tiene. No es cobardía: es el pañol que
fotografié el 21-ago-2026.

Lo que sí cabe aquí, y es lo que entrega este TPA, son tres capas:

1. **Cálculo** de tablero BT: preingeniería IEC 61439 con TAN-Telecom
   (corriente, Icw/Icc, calentamiento, forma, envolvente XL³, expediente
   Excel/PDF).
2. **DSP** sobre señales patrón 3P+N: Clarke αβ0, PLL sobre la tensión
   del PCC, extracción H3/H5/H7 y THDi académico Ih/I1, a 12,8 kHz por
   microbloques.
3. **Lógica segura** de un banco **simulado a 24 V / 120 W** (máquina de
   estados, E-stop enclavado, sin salidas físicas) y un procedimiento de
   laboratorio a **24 VDC** con la wanptek KPS305D (0–30 V / 0–5 A, punto
   24,0 V) y el Gratten GA1102CAL (100 MHz, 2 canales, CSV USB).

El fenómeno se estudia. La compensación **no** se inyecta a la red. El
software no genera PWM ni manda contactores. El HIL declara
`physical_outputs_available = false` siempre. La KPS305D topea a 30 V:
48 V no es medio de prueba de este TPA.

## Objetivo general

Demostrar, con archivos y tests de este repositorio, que un CFT puede
aproximar el problema 3P+N con cálculo auditable, DSP sobre patrón y
SIL a 24 V, sin fingir un ensayo industrial que el pañol no permite.

## Objetivos específicos (medibles)

1. El DSP de `tests/test_dsp.py` sigue a los patrones de
   `dsp/patterns.py` con `REL_TOL = 0.12`.
2. TAN-Telecom genera un prediseño small/medium con Icw, ΔT y XL³, y
   `tan_telecom/tests/` pasa.
3. La FSM de `power_stage/controller.py` llega a RUN y no rearma sola
   tras E-stop u OVERCURRENT; el flag de salidas físicas es false.
4. Tres vistas (Monitor, TAN, Banco 24 V) arrancan con
   `python hil_app.py`, sin Docker.
5. El pañol queda documentado (inventario, procedimiento, protocolo,
   bitácora). La campaña CSV firmada es PLUS, no requisito: un DC de
   24 V no prueba H3.

## Hipótesis de trabajo

Si el DSP sigue a la señal patrón dentro de la tolerancia de
`tests/test_dsp.py` y la FSM no rearma sola, el TPA cumple. El CSV del
Gratten, cuando exista, demuestra la cadena de archivos (Mean ≈ 24 V),
no el espectro.

El alcance está congelado en `docs/ALCANCE_TPA_CFT_PAILLACO.md`. No se
abre a 400 V sin un TPA nuevo.

---

*Andres Barbudo Rodriguez — CFT Paillaco*
