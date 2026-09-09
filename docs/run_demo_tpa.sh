#!/usr/bin/env bash
# Receta de demo TPA sin Docker.
# Autor: Andres Barbudo Rodriguez — CFT Paillaco
# No energiza la KPS305D. No usa 48 V ni 400 V de ensayo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
PY="${PYTHON:-python3}"

echo "TPA CFT Paillaco — demo sin Docker"
echo "  CASO A/C  dashboard:  $PY hil_app.py   → http://localhost:8080"
echo "  CASO B    TAN small:  se genera ahora (no toca output/web/)"
echo

"$PY" -m tan_telecom --example small --output ./output/tpa/demo_defensa -v

echo
echo "Listo CASO B → output/tpa/demo_defensa/"
echo "Para A y C, en otra terminal:"
echo "  PYTHONPATH=. $PY hil_app.py"
echo "No decir: medimos la red del CFT / tablero construido / 48 V reales."
