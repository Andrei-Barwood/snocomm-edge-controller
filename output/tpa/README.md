# Índice de entrega TPA — `output/tpa/`

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  
**Fecha:** 23-ago-2026

Paquete de evidencias de software. **No es un ensayo a 400 V, 48 V, 500 kW
ni ~700 A.** El banco físico del TPA es 24 VDC (wanptek KPS305D + Gratten
GA1102CAL). El HIL es 24 V / 120 W simulados. El caso TAN usa 400 V solo
como tensión de **cálculo** IEC 61439, no como medio de prueba.

Receta pytest: `docs/EVIDENCIAS_TPA.md` sección 1.

---

## Archivos en esta carpeta

| Archivo | Qué prueba | Fecha | Origen |
|---|---|---|---|
| `pytest.txt` | Suite `pytest tests tan_telecom/tests -q` (incluye `test_tpa_smoke`) | 23-ago-2026 | generado en esta entrega |
| `tan_small/TT-S-20260821-154807_informe.html` | Prediseño TAN **small** (45 kW, 4 racks). No es tablero construido. | 21-ago-2026 | `tan_telecom` → `output/tpa/tan_small/` |
| `tan_small/TT-S-20260821-154807_resumen.pdf` | Mismo caso small, PDF | 21-ago-2026 | idem |
| `tan_ejemplo_origen_web.html` | Copia de un informe TAN de la vista web | 21-ago-2026 | `output/web/TT-M-20260821-154033_informe.html` |
| `tan_ejemplo_origen_web.pdf` | Copia del PDF asociado | 21-ago-2026 | `output/web/TT-M-20260821-154033_resumen.pdf` |
| `ORIGEN_COPIAS.txt` | Declaración de origen de las copias | 21-ago-2026 | esta carpeta |

---

## Documentos del repo (enlaces relativos)

| Documento | Estado |
|---|---|
| [Informe de evidencias](../../docs/INFORME_EVIDENCIAS_TPA.md) | hecho |
| [Alcance congelado](../../docs/ALCANCE_TPA_CFT_PAILLACO.md) | hecho |
| [Matriz SIL](../../docs/MATRIZ_SIL_TPA.md) | hecho |
| [Bitácora de laboratorio](../../docs/BITACORA_LABORATORIO_TPA.md) | plantilla (campaña física pendiente) |
| [Casos de demo](../../docs/CASOS_DEMO_DEFENSA.md) | hecho |
| [Receta pytest](../../docs/EVIDENCIAS_TPA.md) | §1 |
| [Esqueleto de memoria](../../docs/memoria/README.md) | portada + índice |

No hay dumps de osciloscopio. CSV de ejemplo (no campaña real):
`acquisition/panol_24v_gratten_example.csv` (< 200 líneas).

---

*Andres Barbudo Rodriguez — CFT Paillaco — 23-ago-2026*
