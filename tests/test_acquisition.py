"""Importación de CSV de osciloscopio y JSON de central."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from acquisition.parser import parse_csv, parse_json_campaign
from acquisition.pipeline import example_scope_csv, process_campaign
from hil_app import app
from project_store import store
import acquisition_service

PANOL_24V_CSV = (
    Path(__file__).resolve().parents[1] / "acquisition" / "panol_24v_gratten_example.csv"
)


def test_parse_scope_csv_maps_channels():
    table = parse_csv(example_scope_csv())
    assert table.mapping["time"] == "Time"
    assert table.mapping["ia"] == "CH1"
    assert table.mapping["in"] == "CH4"
    assert table.columns["CH1"].size > 1000


def test_parse_european_csv_semicolon_decimal_comma():
    text = "t;Ia\n0,0000;1,5\n0,0001;1,6\n0,0002;1,4\n"
    table = parse_csv(text)
    assert table.delimiter == ";"
    assert table.mapping["ia"] == "Ia"
    assert table.columns["Ia"][0] == 1.5


def test_process_scope_csv_runs_dsp():
    table = parse_csv(example_scope_csv())
    result = process_campaign(table, filename="demo.csv")
    assert result.telemetry["source"] == "imported"
    assert result.telemetry["i1_rms"] > 1.0
    assert result.telemetry["thdi"] > 5.0
    assert result.meta["mode"] == "waveforms"


def test_registers_only_json():
    table, registers = parse_json_campaign(
        {"registers": {"thdi": 14.2, "i1_rms": 20.0, "h3_rms": 2.0, "h5_rms": 1.0, "h7_rms": 0.5}}
    )
    assert table is None
    result = process_campaign(table, registers, filename="emdx.json")
    assert result.meta["mode"] == "registers"
    assert result.telemetry["thdi"] == 14.2
    assert result.telemetry["raw_waveform"] == [0.0] * 128


def test_import_csv_via_api_feeds_project():
    acquisition_service._session["last"] = None
    store.configure("hil", "none", "hil_simulation")
    client = TestClient(app)
    files = {"file": ("scope.csv", example_scope_csv().encode("utf-8"), "text/csv")}
    response = client.post("/api/acquisition/import", files=files)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["telemetry"]["thdi"] > 0
    runtime = client.get("/api/runtime").json()
    assert runtime["acquisition"] == "imported"
    project = client.get("/api/project").json()
    assert project["links"]["observed_thdi"] == body["telemetry"]["thdi"]


def test_live_json_endpoint_and_clear():
    client = TestClient(app)
    payload = {
        "source": "emdx3",
        "registers": {"THDi": 11.0, "I1_rms": 15.0, "h3": 1.5, "h5": 0.8, "h7": 0.4},
    }
    response = client.post("/api/acquisition/live", json=payload)
    assert response.status_code == 200
    assert response.json()["telemetry"]["thdi"] == 11.0
    cleared = client.post("/api/acquisition/clear")
    assert cleared.status_code == 200
    assert cleared.json()["acquisition"] != "imported"
    last = client.get("/api/acquisition/last")
    assert last.status_code == 404


def test_parse_panol_24v_gratten_csv():
    text = PANOL_24V_CSV.read_text(encoding="utf-8")
    auto = parse_csv(text)
    assert "Time" in auto.headers
    assert "CH1" in auto.headers
    assert "CH4" not in auto.headers
    assert auto.mapping["time"] == "Time"
    assert auto.mapping["ia"] == "CH1"
    mapped = parse_csv(text, mapping={"time": "Time", "va": "CH1"})
    assert mapped.mapping["va"] == "CH1"
    assert "ia" not in mapped.mapping
    mean = float(mapped.columns["CH1"].mean())
    assert 23.5 <= mean <= 24.5


def test_preview_lists_headers():
    client = TestClient(app)
    files = {"file": ("scope.csv", example_scope_csv().encode("utf-8"), "text/csv")}
    response = client.post("/api/acquisition/preview", files=files)
    assert response.status_code == 200
    body = response.json()
    assert "Time" in body["headers"]
    assert body["suggested_mapping"]["ia"] == "CH1"
