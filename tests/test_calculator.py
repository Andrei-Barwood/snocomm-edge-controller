"""Calculadora comparativa: 24 plantillas, CSV de pañol y PDF."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from calculator.engine import analyze, list_templates
from calculator.stats import summarize_csv
from calculator.templates import TEMPLATES
from hil_app import app

PANOL = Path(__file__).resolve().parents[1] / "acquisition" / "panol_24v_gratten_example.csv"


def test_there_are_exactly_24_templates():
    assert len(TEMPLATES) == 24
    assert len(list_templates()) == 24
    ids = [item["id"] for item in TEMPLATES]
    assert ids == [f"T{i:02d}" for i in range(1, 25)]
    for item in TEMPLATES:
        assert item["fields"]
        assert item["iec"]
        assert item["voice"]


def test_panol_csv_is_24v_bus():
    summary = summarize_csv(PANOL.read_text(encoding="utf-8"), PANOL.name)
    assert summary["domain"] == "dc_24v_scope"
    assert 23.0 <= summary["v_mean"] <= 25.0
    assert summary["v_channel"] == "CH1"


def test_analyze_t01_aligns_with_24v_design():
    csv_text = PANOL.read_text(encoding="utf-8")
    result = analyze("T01", {"v_nom": 24, "ripple_max_pct": 2}, csv_after=csv_text, name_after="panol.csv")
    assert result["status"] == "EN_LINEA"
    assert result["measured"] is not None
    assert abs(result["measured"] - 24) < 1
    assert "61439" in result["iec_note"]
    assert "certificado" not in result["narrative"].lower()


def test_api_templates_legal_and_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr("calculator_service.OUTPUT", tmp_path)
    client = TestClient(app)
    templates = client.get("/api/calculator/templates").json()
    assert templates["count"] == 24
    legal = client.get("/api/calculator/legal").json()
    assert legal["title"].startswith("Legislaciones")
    assert "SEC" in " ".join(p for s in legal["sections"] for p in s["body"])
    csv_bytes = PANOL.read_bytes()
    response = client.post(
        "/api/calculator/analyze",
        data={"template_id": "T01", "params": '{"v_nom": 24, "ripple_max_pct": 2}'},
        files={"csv_after": ("panol.csv", csv_bytes, "text/csv")},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["pdf"]["url"].endswith(".pdf")
    pdf = client.get(body["pdf"]["url"])
    assert pdf.status_code == 200
    assert pdf.content[:4] == b"%PDF"
    assert len(pdf.content) > 500


def test_demo_csvs_for_exam():
    from calculator.examples.catalog import CATALOG, EXAMPLES_DIR

    assert len(CATALOG) == 9
    for item in CATALOG:
        path = EXAMPLES_DIR / item["file"]
        assert path.is_file(), item["file"]
        summary = summarize_csv(path.read_text(encoding="utf-8"), path.name)
        assert summary["samples"] >= 100

    estable = (EXAMPLES_DIR / "demo_01_bus_24v_estable.csv").read_text(encoding="utf-8")
    caida = (EXAMPLES_DIR / "demo_03_bus_24v_caida.csv").read_text(encoding="utf-8")
    antes = (EXAMPLES_DIR / "demo_04_antes_ilim.csv").read_text(encoding="utf-8")
    despues = (EXAMPLES_DIR / "demo_05_despues_ilim.csv").read_text(encoding="utf-8")
    assert analyze("T01", {"v_nom": 24, "ripple_max_pct": 2}, csv_after=estable)["status"] == "EN_LINEA"
    assert analyze("T01", {"v_nom": 24, "ripple_max_pct": 2}, csv_after=caida)["status"] == "ATENCION"
    pair = analyze(
        "T20",
        {"mejora_min_pct": 10, "eje": "rizado"},
        csv_before=antes,
        csv_after=despues,
    )
    assert pair["status"] == "EN_LINEA"

    client = TestClient(app)
    listing = client.get("/api/calculator/examples").json()
    assert len(listing["examples"]) == 9
    csv = client.get("/api/calculator/examples/demo_01_bus_24v_estable.csv")
    assert csv.status_code == 200
    assert b"CH1" in csv.content
    assert client.get("/api/calculator/examples/../secrets.csv").status_code == 404
