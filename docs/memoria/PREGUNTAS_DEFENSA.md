# Banco de preguntas de defensa

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  
**Tono:** técnico de CFT, no brochure. Veinte respuestas para memorizar.

---

### 1. ¿Por qué no ensayaste a 400 V si tu licencia es clase A?

La clase A habilita trabajos de baja tensión en el contexto legal que
corresponda. No fabrica un banco de ~700 A ni 500 kW en el CFT Paillaco.
El alcance congelado dice: medio de prueba ≠ habilitación. Este TPA es
24 VDC (KPS305D 0–30 V / 0–5 A). 400 V queda para un TPA nuevo.

### 2. ¿Ese THDi sirve para la SEC?

No. Es Ih/I1 de H3+H5+H7 sobre la señal que el DSP ve, tolerancia 12 %
en `tests/test_dsp.py`. No es IEC 61000-4-7. La leyenda del Monitor dice
«Académico · no IEC/SEC».

### 3. ¿El Raspberry / PC genera el PWM?

No. `physical_outputs_available` es false siempre. Los indicadores de PWM
y contactor son booleanos del HIL. Este software no manda GPIO ni
compuertas.

### 4. ¿Python es tiempo real?

No. El README: Python sobre un SO general **no** garantiza hard
real-time. El DSP corre por microbloques a 12,8 kHz. Lo declaro como
límite, no como defecto escondido.

### 5. ¿Construiste el tablero TAN?

No. TAN-Telecom es prediseño IEC 61439. El Excel/PDF es expediente de
cálculo. `tan_telecom/tests/` verifica reglas, no un tablero ensayado.

### 6. ¿El banco de 24 V está energizado por este software?

No. El HIL simula 24 V / 120 W. La KPS305D se enciende a mano, con Ilim
antes de V, y clase A si está en I. El corte es el switch I/O, no el PC.

### 7. ¿Qué prueba el CSV del Gratten GA1102CAL y qué no?

Prueba la cadena fuente → scope → pendrive → Monitor (Mean ≈ 24 V si
CH1 → va). No prueba H3/H5/H7: es DC, no hay I1 senoidal. El DSP de
armónicos se defiende con `dsp/patterns.py`.

### 8. ¿Por qué el TPA no es 48 V?

La KPS305D topea a 30 V. No hay segunda fuente fotografiada. 48 V está
fuera del alcance, igual que 400 V. El HIL usa los mismos 24 V / 5 A /
120 W.

### 9. ¿El Gratten es un analizador de red?

No. Es un DSO 100 MHz, 2 canales, 1 GSa/s. Sirve para DC 24 V y rizado.
No es IEC 61000. No captura 3P+N a la vez.

### 10. ¿Puedes ver H3 en el scope con 24 VDC?

No. Un DC plano no tiene fundamental senoidal ni H3. Si el dashboard
tira un THDi alto sobre ese CSV, es artefacto. H3 se muestra con el
patrón sintético.

### 11. ¿Qué haces si el pendrive no monta el CSV en el examen?

BMP o PRINT de la pantalla del Gratten y el DSP sigue en CASO A
(sintético). Lo digo en voz alta: “el USB falló; la evidencia de
armónicos sigue siendo el patrón”.

### 12. ¿Qué pasa si alguien da enable en FAULT?

El software rechaza. Tras OVERCURRENT hay que `reset_fault` a mano.
Tras E-stop, primero `release_estop`. No hay rearranque automático.

### 13. ¿Dónde está el E-stop, en software o en cable?

En el HIL: latch de software. En el pañol: no hay seta fotografiada; el
corte es el switch I/O de la KPS305D. El PC no anula ese switch.

### 14. ¿Qué norma usaste de verdad en el código?

IEC 61439-1/2 en `tan_telecom` (cálculo, no certificado). RIC 04 p.5.3
solo como nota de neutro si hay carga armónica. 62477-1 / E-stop como
criterio de diseño SIL. 61000: no se midió.

### 15. ¿Por qué H3 en el neutro?

H3 es secuencia cero: las tres fases coinciden y el neutro lleva cerca
de tres veces esa componente. Por eso un AHF de telecom se piensa 3P+N.
Yo no inyecto esa corriente; la extraigo del patrón.

### 16. ¿Qué harías si mañana aparece un analizador certificado?

Una campaña en el PCC, import al Monitor, y dejar de vender el THDi
académico como medición. El DSP de tests seguiría siendo el patrón.
No cambio el alcance a 400 V sin medio de prueba.

### 17. ¿Este software se puede vender como AHF?

No. Licencia MIT académica. No hay conformidad de producto, ni PWM
real, ni inyección. Es TPA de CFT, no un filtro de 50–100 A.

### 18. ¿Qué es `physical_outputs_available = false`?

Un flag del snapshot HIL: este proceso no tiene backend de GPIO.
Se afirma en POWER_OFF, RUN, ESTOP y FAULT (`tests/test_power_stage.py`).

### 19. ¿Por qué Ilim antes de subir V?

Salvaguarda de la KPS305D. Si la carga pide más que 0,50 A, pasa a C.C.
Eso no es un AHF en falla. Protocolo de las primeras líneas: 400 V y
48 V prohibidos.

### 20. ¿Qué hago si la comisión pide 400 V en la mesa?

Leo el alcance congelado: este CFT no tiene banco de ~700 A. La clase A
no lo inventa. Ofrezco Monitor (patrón), TAN (prediseño) y SIL 24 V.
No improviso un puente.

---

*Andres Barbudo Rodriguez — CFT Paillaco — 23-ago-2026*
