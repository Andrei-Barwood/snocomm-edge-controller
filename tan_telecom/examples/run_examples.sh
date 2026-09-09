#!/usr/bin/env bash
# Ejecuta los tres ejemplos oficiales de TAN-Telecom.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python main.py --example small  --output ./output/small  -v
python main.py --example medium --output ./output/medium -v
python main.py --example large  --output ./output/large  -v
echo "OK: ejemplos small/medium/large generados en ./output/"
