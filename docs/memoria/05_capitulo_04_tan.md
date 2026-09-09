# 4. Preingeniería TAN

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

TAN-Telecom prediseña tableros para nodos telecom. **No se construyó
ningún tablero en este TPA.**

**Entradas:** potencia kW, número de racks, redundancia (N / N+1 / 2N),
IP mínimo, flags de carga armónica y sísmico.

**Reglas:** `calculations.py` (In, Icw/Icc, ΔT) y `rules.py` (familia
TT-S/M/E, forma IEC 61439-2, envolvente XL³, verificaciones Anexo D, BOM).

**Salidas:** Excel, PDF, HTML, Markdown, JSON, CSV de BOM.

Comando de defensa (no escribe en `output/web/`):

```bash
PYTHONPATH=. python -m tan_telecom --example small --output ./output/tpa/demo_defensa -v
```

## Caso real del repo: small

Artefacto: `output/tpa/tan_small/TT-S-20260821-154807_memoria.md`.

| Parámetro | Valor del archivo |
|---|---|
| Potencia / racks / redundancia | 45,0 kW · 4 · N |
| In base / selección | 75,97 A / **80,0 A** |
| Icc / Icw | **16,0 / 16,0 kA** |
| ΔT estimado | **10,7 °C** (límite 30,0 °C) |
| Envolvente | XL³ 160 IP55 |
| Forma | 2b (familia TT-S) |

La fórmula usa `V = 400 V` como tensión de **cálculo**
(`In = P·1000/(√3·V·cosφ·η)`). Eso no es un ensayo a 400 V en el pañol.

`carga_armonica` es false en este small: no aparece la nota RIC 04 p.5.3.
Esa nota sí sale en un medium con el flag armónico (`project_store.py`).

Los tests `tan_telecom/tests/test_calculations.py` y `test_rules.py`
verifican el cálculo, no un tablero de laboratorio.

---

*Andres Barbudo Rodriguez — CFT Paillaco*
