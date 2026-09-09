# 2. Marco normativo usado

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

Este capítulo es literal: qué **aplica el código**, no qué “cumple el
equipo”. Ningún aparato de este TPA está certificado.

## IEC 61439-1/2

`tan_telecom/calculations.py` y `rules.py` usan la norma como **regla de
cálculo**: In, normalización de corriente, Icw/Icc de catálogo XL³,
estimación de calentamiento (referencia a §10.10 como estimación, no
como ensayo de tipo), forma de separación IEC 61439-2, tabla de
verificaciones Anexo D.

Lo que el código **no** hace: ensayo de tablero en laboratorio, sello de
ensamblador, certificación de producto.

## RIC

Solo se cita el párrafo que el proyecto escribe cuando hay carga
armónica: **RIC 04 p.5.3** (neutro al menos 50 % mayor que las fases con
cargas no lineales, salvo excepción de filtro en la carga). Está en
`project_store.py` (`ric04_neutral_note`) y pasa al Excel/PDF TAN si
`carga_armonica` es verdadera. El caso **small** de entrega (sin flag
armónico) no dispara esa nota.

## IEC 62477-1 e ISO 13850

Criterio de **diseño** del SIL (convertidor / E-stop): latch, no
rearranque automático, salidas lógicas a false. No hay certificado
62477 ni de parada de emergencia de seta (no fotografiada). El corte
físico del pañol es el switch I/O de la KPS305D.

## IEC 61000

Fuera de alcance de medición. El Gratten no es analizador. El THDi del
dashboard no es 61000-4-7.

## Tabla requisito | tratamiento | vacío

| Requisito | Cómo lo trata este TPA | Vacío |
|---|---|---|
| IEC 61439-1/2 cálculo In, Icw, forma, XL³ | `tan_telecom` aplica la regla | Ensayo de tipo, tablero construido |
| IEC 61439 §10.10 calentamiento | ΔT estimado en código | Ensayo de elevación de temperatura |
| RIC 04 p.5.3 neutro | Nota en prediseño si hay armónicos | Memoria RIC de obra |
| IEC 62477-1 / ISO 13850 | Latch SIL, E-stop lógico | Certificado de convertidor / seta física |
| IEC 61000 (EMC, 4-7) | Declarado fuera | Medición certificada |
| SEC | No se afirma conformidad | Informe SEC |

---

*Andres Barbudo Rodriguez — CFT Paillaco*
