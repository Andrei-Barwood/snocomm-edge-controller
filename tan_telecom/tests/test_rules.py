"""Tests del motor de decisión y generación de entregables."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tan_telecom.models import ProjectInputs, Redundancia, FormaSeparacion
from tan_telecom.rules import run_design, select_separation_form
from tan_telecom.calculations import compute_electrical
from tan_telecom.export import export_bundle
import json


def test_small_prefers_2b():
    inputs = ProjectInputs(45, 4, Redundancia.N, ip_minimo=54)
    elec = compute_electrical(inputs)
    sep = select_separation_form(inputs, elec)
    assert sep.forma == FormaSeparacion.F2B
    assert sep.familia_tan == "TT-S"


def test_medium_prefers_3b():
    inputs = ProjectInputs(120, 8, Redundancia.N1, ip_minimo=54, carga_armonica=True)
    result = run_design(inputs)
    assert result.separation.forma in {FormaSeparacion.F3B, FormaSeparacion.F4B}
    assert result.enclosure.codigo in {"XL3-160", "XL3-800", "XL3-4000", "XL3-6300"}
    assert len(result.verifications) >= 13
    assert len(result.bom) >= 8


def test_export_artifacts(tmp_path):
    inputs = ProjectInputs(45, 4, Redundancia.N, output_dir=str(tmp_path))
    result = run_design(inputs)
    extras = {
        "shared_project_id": "SNO-TEST",
        "observed_harmonics": {"thdi": 18.0, "h3_rms": 10.0, "h5_rms": 5.0, "h7_rms": 2.0},
        "compensation_current_a": 11.36,
    }
    paths = export_bundle(result, tmp_path, extras=extras)
    assert set(paths) == {"xlsx", "pdf", "json", "md", "html", "csv"}
    assert paths["xlsx"].stat().st_size > 1000
    assert paths["pdf"].read_bytes()[:4] == b"%PDF"
    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert payload["shared_project_id"] == "SNO-TEST"
    assert "TT-S" in paths["md"].read_text(encoding="utf-8") or result.project_id in paths["md"].read_text(
        encoding="utf-8"
    )
    html = paths["html"].read_text(encoding="utf-8")
    assert "Verificaciones" in html and result.enclosure.codigo in html
    csv_text = paths["csv"].read_text(encoding="utf-8")
    assert "codigo" in csv_text and result.bom[0].codigo in csv_text
