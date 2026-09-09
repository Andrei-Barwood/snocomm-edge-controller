# Evidencias del TPA

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  
**Índice de entrega:** `output/tpa/README.md`

Esto no es un ensayo a 400 V, 500 kW ni ~700 A. El banco físico es 24 VDC
(wanptek KPS305D + Gratten GA1102CAL). El HIL es 24 V / 120 W simulados.

---

## 1. Suite de regresión

Comando exacto, sin Docker, desde la raíz del repositorio:

```bash
pytest tests tan_telecom/tests -q
```

En este entorno, si el paquete no está instalado:

```bash
PYTHONPATH=. .venv/bin/pytest tests tan_telecom/tests -q
```

Archivar la salida en `output/tpa/pytest.txt`:

```bash
PYTHONPATH=. .venv/bin/pytest tests tan_telecom/tests -q > output/tpa/pytest.txt 2>&1
```

La carpeta `output/tpa/` es el índice de entrega. Incluye `pytest.txt` y
un caso TAN **small**. El informe narrativo de evidencias
(`docs/INFORME_EVIDENCIAS_TPA.md`) y los casos de demo de defensa son el
siguiente entregable.

---

*Andres Barbudo Rodriguez — CFT Paillaco — 21-ago-2026*
