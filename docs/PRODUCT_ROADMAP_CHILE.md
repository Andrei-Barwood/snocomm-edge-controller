# Ruta de producto — AHF modular para Chile

## Objetivo comercial

El límite de 500 kW corresponde a la instalación atendida, no a la potencia
del convertidor. El producto debe especificarse por corriente de compensación.

Objetivo inicial recomendado:

```text
Red: 400/230 VAC, 50 Hz, 3P+N
Módulo: 50–100 A de corriente compensatoria
Arquitectura: inversor de cuatro ramas
Escala: módulos en paralelo coordinados por un maestro
```

La rama de neutro es importante para cargas de telecomunicaciones monofásicas,
desequilibrio y armónicos de secuencia cero.

## Etapas de madurez

| Fase | Resultado | Prohibición de avance |
|---|---|---|
| HIL 24 V / 120 W | Estados, fallas y planta simulada (TPA) | Ninguna salida física |
| 24 V pañol (KPS305D) | Captura Gratten + CSV; Ilim | Sin 48 V, sin red de 400 V |
| 48 V / 500 W (fuera de este TPA) | Solo si aparece una fuente que lo permita | Sin red de 400 V |
| Alpha | Módulo de corriente reducida | Sin instalación de cliente |
| Beta | Módulo 50–100 A y gabinete | Sólo banco autorizado |
| Piloto | Sistema modular supervisado | Revisión independiente obligatoria |
| Producto | Ensayos, fabricación y trazabilidad | Sin venta antes de conformidad |

## Mediciones sin analizador propio

Durante el TPA se usan equipos del pañol CFT Paillaco:

- wanptek KPS305D (0–30 V / 0–5 A, punto 24,0 V, Ilim).
- Gratten GA1102CAL (100 MHz, 2 canales, CSV USB).
- Carga resistiva P < 120 W.
- Punta pasiva CH1 (1x/10x).

48 V no es etapa de este TPA: la KPS305D topea a 30 V.

Para caracterizar una instalación real no es necesario comprar inicialmente un
analizador de calidad de energía. Se puede arrendar, contratar una campaña de
medición o colaborar con un laboratorio. La selección final del AHF sí debe
basarse en mediciones trazables en el punto de conexión común.

## Paquete mínimo de ingeniería

Antes de diseñar el módulo de 400 V deben existir:

- Especificación de requisitos eléctricos y ambientales.
- Diagrama unilineal y análisis de riesgos.
- Espectro armónico de casos representativos.
- Cálculo de semiconductores, DC-link y filtro de acoplamiento.
- Coordinación de protecciones y corriente de cortocircuito admisible.
- Coordinación de aislamiento, distancias y puesta a tierra.
- Simulación térmica y plan de refrigeración.
- Diseño para EMC y ensayos de inmunidad/emisión.
- FMEA y matriz de trazabilidad de requisitos.
- Procedimientos de producción, commissioning y mantenimiento.

## Referencias principales

- IEC 62477-1: seguridad de convertidores electrónicos de potencia.
- IEC 60947: aparamenta, contactores y dispositivos de control.
- IEC 61000-6-2 / 61000-6-4: inmunidad y emisiones industriales.
- ISO 13850 e IEC 60947-5-5: parada de emergencia.
- Pliegos RIC y reglamentación SEC aplicables a la instalación chilena.

La licencia de instalador habilita trabajos dentro de su alcance, pero no
reemplaza la evaluación de conformidad del producto ni la revisión especializada
de electrónica de potencia.
