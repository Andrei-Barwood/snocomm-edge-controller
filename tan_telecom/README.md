# TAN-Telecom

**Herramienta CLI profesional** para el **diseño paramétrico** y la **generación automática de documentación** de tableros eléctricos estandarizados tipo **TAN** (IEC 61439-1 & 2), orientados a **nodos de telecomunicaciones** e infraestructura informática.

Proyecto de titulación / TPA — CFT Electricidad.

| | |
|:---|:---|
| **Nombre** | TAN-Telecom |
| **Paquete** | `tan_telecom` |
| **Lenguaje** | Python 3.10+ |
| **Interfaz** | CLI (`typer` + `rich`) |
| **Norma de referencia** | IEC 61439-1 & 2 |
| **Referencia constructiva** | Familia XL³ / filosofía TAN (Legrand) |

---

## 1. Problema que resuelve

En nodos de telecomunicaciones (POP, edge, salas técnicas) el proyectista debe:

1. Estimar corrientes y exigir Icw/Icc coherentes.
2. Elegir **envolvente** y **forma de separación interna** (1…4b) con criterio técnico.
3. Documentar **verificaciones de diseño**, BOM y parámetros de placa.

Esa documentación suele hacerse a mano y con criterios poco trazables. **TAN-Telecom** captura parámetros, aplica reglas defendibles y genera **Excel + PDF + JSON** de forma reproducible.

---

## 2. Requisitos previos

- Python **3.10+**
- `pip` / entorno virtual recomendado
- Sistema operativo: macOS, Linux o Windows

---

## 3. Instalación

```bash
cd tan_telecom
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Instalación editable (opcional):

```bash
pip install -e .
```

---

## 4. Uso rápido

```bash
# Ayuda
python main.py --help

# Tres ejemplos oficiales
python main.py --example small  --output ./output/small  -v
python main.py --example medium --output ./output/medium -v
python main.py --example large  --output ./output/large  -v

# Configuración libre
python main.py \
  --potencia-kw 90 \
  --num-racks 6 \
  --redundancia N+1 \
  --ip-minimo 54 \
  --carga-armonica \
  --output ./output/mi_proyecto \
  -v
```

También:

```bash
# Desde el directorio padre del paquete
python -m tan_telecom --example small --output ./tan_telecom/output/small
```

---

## 5. Parámetros CLI

| Parámetro | Tipo | Obligatorio | Default | Descripción |
|-----------|------|:-----------:|---------|-------------|
| `--potencia-kw` | float | Sí* | – | Potencia total instalada [kW] |
| `--num-racks` | int | Sí* | – | Número de racks / salidas |
| `--redundancia` | choice | Sí* | – | `N`, `N+1`, `2N` |
| `--ip-minimo` | int | No | `54` | IP mínimo: 30, 31, 40, 41, 54, 55, 65, 66 |
| `--carga-armonica` | flag | No | False | Cargas no lineales (armónicos) |
| `--sismico` | flag | No | False | Resistencia sísmica (IEC 60068-3-3 / UBC Z4) |
| `--output` | path | No | `./output` | Carpeta de salida |
| `--example` | choice | No | – | `small` \| `medium` \| `large` |
| `--verbose` / `-v` | flag | No | False | Justificaciones detalladas |
| `--version` | flag | No | – | Muestra versión |

\* No obligatorios si se usa `--example`.

---

## 6. Ejemplos predefinidos

| Nombre | Potencia | Racks | Redundancia | IP | Armónicos | Sísmico |
|--------|----------|-------|-------------|----|-----------|---------|
| `small` | 45 kW | 4 | N | 54 | No | No |
| `medium` | 120 kW | 8 | N+1 | 54 | Sí | No |
| `large` | 350 kW | 16 | 2N | 55 | Sí | Sí |

Cada ejecución genera:

- `*_documentacion.xlsx` — Verificaciones, BOM, parámetros y hoja del proyecto común  
- `*_resumen.pdf` — Resumen técnico 2–3 páginas  
- `*_config.json` — Configuración versionable  
- `*_memoria.md` — Informe Markdown para el portafolio TPA  
- `*_informe.html` — Informe HTML imprimible  
- `*_bom.csv` — Lista de materiales  

La vista web **Diseño TAN** ofrece los mismos formatos en `/api/tan/report/{xlsx|pdf|json|md|html|csv}`.

---

## 7. Lógica de diseño (resumen)

### 7.1 Corriente nominal

\[
I_n = \frac{P \cdot 1000}{\sqrt{3} \cdot V \cdot \cos\varphi \cdot \eta}
\]

Valores por defecto: \(V = 400\,\mathrm{V}\), \(\cos\varphi = 0{,}9\), \(\eta = 0{,}95\).

Factores de redundancia de diseño:

| Esquema | Factor |
|---------|--------|
| N | 1.00 |
| N+1 | 1.20 |
| 2N | 1.05 (+ arquitectura dual feed documentada) |

La corriente se **normaliza** a la corriente de catálogo superior (63, 80, 100, 125, 160, … A).

### 7.2 RDF, Icc/Icw y calentamiento

- **RDF** según número de circuitos/salidas (1.0 → 0.5).
- **Icc/Icw** estimados por tipología y tamaño (conservadores; no sustituyen estudio de red).
- **ΔT** estimado con modelo térmico de predimensionamiento; criterio de referencia **ΔT < 30 °C** (documento Legrand / práctica BT).

### 7.3 Selección de envolvente XL³

Catálogo tipificado (`data/xl3_catalog.json`):

| Código | I max | Uso típico |
|--------|------:|------------|
| XL³-160 | 160 A | Nodo pequeño / edge ligero |
| XL³-800 | 800 A | POP / mediano |
| XL³-4000 | 4000 A | Multi-rack / dual feed |
| XL³-6300 | 6300 A | Alta potencia |

Prioridad: corriente → Icw/Icc → IP → sísmico → n.º de salidas → menor complejidad.

### 7.4 Forma de separación (IEC 61439-2)

| Escenario | Forma típica | Familia |
|-----------|--------------|---------|
| Nodo pequeño, N, baja densidad | **2b** | TT-S |
| Multi-rack, N+1, armónicos | **3b** | TT-M / TT-E |
| 2N + alta densidad / SLA extremo | **3b** o **4b** | TT-M |

La herramienta **documenta la justificación** en Excel, PDF y consola (`-v`).

### 7.5 Verificaciones de diseño

Hoja Excel alineada a la **tabla de verificaciones de diseño** (IEC 61439-1 Anexo D / página 8 del documento Legrand): artículos 10.2–10.13, métodos Ensayos / Comparación / Evaluación, estado y observaciones.

---

## 8. Estructura del proyecto

```text
tan_telecom/
├── main.py
├── cli.py
├── calculations.py
├── rules.py
├── models.py
├── validators.py
├── generators/
│   ├── excel_generator.py
│   └── pdf_generator.py
├── data/
│   └── xl3_catalog.json
├── examples/
├── tests/
├── README.md
├── requirements.txt
└── pyproject.toml
```

---

## 9. Tests

```bash
pip install pytest
pytest -q
```

---

## 10. Limitaciones y supuestos

- **No** realiza ensayos de laboratorio ni certifica un tablero real con sello TAN de fabricante.
- Icc/Icw son **estimaciones de predimensionamiento**, no un estudio de cortocircuito de red.
- El modelo térmico es **simplificado** (orden de magnitud).
- La BOM es **tipificada** (no cotización comercial ni códigos de catálogo oficiales).
- Selectividad y coordinación de protecciones quedan a cargo del proyectista.
- Alcance orientado a **BT** y nodos de telecomunicaciones / IT.

---

## 11. Referencias

1. IEC 61439-1 — Low-voltage switchgear and controlgear assemblies — General rules.  
2. IEC 61439-2 — Power switchgear and controlgear assemblies (PSC).  
3. Legrand — *Construcción y Certificación de Tableros en conformidad con IEC 61439-1 & 2* (familia XL³, verificaciones, formas de separación, TAN).  
4. IEC 60068-3-3 — Environmental testing (sísmico), cuando aplique.  
5. Memoria técnica del proyecto TPA TAN-Telecom (CFT Electricidad).

---

## 12. Licencia y autoría

Uso académico / profesional de apoyo a ingeniería.  
Autor del TPA: **Andrei Barwood** — CFT Electricidad.
