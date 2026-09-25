# CSV de demostración — examen de titulación

Nueve campañas listas para la pestaña **Calculadora**. Se descargan desde la propia vista o desde `/api/calculator/examples/<archivo>`.

Los dumps de bus 24 V imitan un export del Gratten GA1102CAL (Time, CH1). Las campañas de corriente trifásica son **sintéticas**: el GA1102CAL tiene 2 canales y no captura 3P+N a la vez. En oral se dice exactamente eso.

## Guion sugerido (8–10 min)

1. **T01 + `demo_01_bus_24v_estable.csv`**  
   Formulario en 24 V / 2 % de rizado. Sale *en línea*. Es el caso feliz del rack CFT.

2. **T01 + `demo_03_bus_24v_caida.csv`**  
   Misma plantilla, bus en 21,4 V. Sale *priorizar una revisión*. Ahí se habla de Ilim, carga del rack y condiciones de servicio IEC 61439-1.

3. **T01 + `demo_02_bus_24v_rizado.csv`**  
   Media 24 V (sigue cerca del diseño) con rizado 120 Hz alto. La sugerencia del motor apunta al filtrado, no a cambiar la envolvente.

4. **T20 + anterior `demo_04_antes_ilim.csv` + nuevo `demo_05_despues_ilim.csv`**  
   Eje **rizado**. Misma sonda, mismo bornes, Ilim ajustada. Sale *en línea* porque el rizado baja. Es el mejor momento para el PDF con dos ondas.

5. **T02 + `demo_07_corriente_justa.csv`** (opcional `demo_06` antes)  
   In de prediseño 63 A. 61 A queda en línea; 50 A abre la conversación de reserva.

6. Cierre: pestaña **Legislación** en una frase y listo.

`demo_08` (T09, desequilibrio) y `demo_09` (2 canales Va/Ia) quedan de reserva si la comisión pregunta por fases o por el Gratten de 2 canales.

Regenerar: `python -m calculator.examples.generate`
