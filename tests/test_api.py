"""API del proyecto común, TAN enriquecido y paquete del banco."""

from __future__ import annotations

from fastapi.testclient import TestClient

from hil_app import app
from project_store import store


def test_runtime_and_bench_package():
    client = TestClient(app)
    runtime = client.get("/api/runtime").json()
    assert runtime["launch_mode"] == "hil"
    assert runtime["acquisition"] == "none"
    assert runtime["hardware"] == "hil_simulation"
    pack = client.get("/api/bench/package").json()
    assert pack["acceptance"]
    assert "24 V" in pack["voltage_class"]
    assert "48" not in pack["voltage_class"]
    assert pack["source"]["instrument"] == "wanptek KPS305D"
    assert pack["source"]["work_point_v"] == 24.0
    assert pack["scope"]["instrument"] == "Gratten GA1102CAL"
    assert "48 V" in pack["forbidden"]
    assert "400 V" in pack["forbidden"]
    assert "500 kW" in pack["forbidden"]
    assert "~700 A" in pack["forbidden"]
    assert pack["panol"] == "Pañol CFT Paillaco"
    assert "CFT Paillaco" in pack["title"]
    assert pack["physical_outputs_available"] is False
    assert pack["sil"]["overvoltage_trip_v"] == 29.0
    assert pack["sil"]["voltage_v"] == 24.0
    assert "24 V" in pack["layers"]["A"]
    assert "KPS305D" in pack["layers"]["B"]
    assert "GA1102CAL" in pack["layers"]["B"]
    assert "48 V" in pack["layers"]["C"]
    assert "400 V" in pack["layers"]["C"]
    bom_text = " ".join(row["item"] for row in pack["cft_bom"])
    assert "KPS305D" in bom_text
    assert "GA1102CAL" in bom_text
    assert "Pañol CFT Paillaco" in {row["source"] for row in pack["cft_bom"]}
    assert "diferencial" not in bom_text.lower()
    assert "24–48" not in bom_text and "24-48" not in bom_text
    assert "fuente 24–48" not in bom_text.lower()


def test_tan_design_attaches_shared_project():
    store.reset()
    store.update_monitor(
        {
            "thdi": 18.0,
            "thdi_method": "Ih(3+5+7) / I1 · 100",
            "i1_rms": 70.0,
            "h3_rms": 10.0,
            "h5_rms": 5.0,
            "h7_rms": 2.0,
            "in_rms": 30.0,
        }
    )
    client = TestClient(app)
    response = client.post(
        "/api/tan/design",
        json={
            "potencia_kw": 120,
            "num_racks": 8,
            "redundancia": "N+1",
            "ip_minimo": 54,
            "carga_armonica": True,
            "sismico": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["shared_project_id"]
    assert body["observed_harmonics"]["thdi"] == 18.0
    assert body["compensation_current_a"] > 0
    project = client.get("/api/project").json()
    assert project["links"]["thdi_feeds_tan"] is True
    assert project["links"]["dsp_commands_bank"] is False
    reports = body["reports"]
    assert set(reports) == {"xlsx", "pdf", "json", "md", "html", "csv"}
    pdf = client.get("/api/tan/report/pdf")
    assert pdf.status_code == 200
    assert pdf.content[:4] == b"%PDF"
    xlsx = client.get("/api/tan/report/xlsx")
    assert xlsx.status_code == 200
    assert xlsx.content[:2] == b"PK"
    markdown = client.get("/api/tan/report/md")
    assert markdown.status_code == 200
    assert "THDi" in markdown.text
    html = client.get("/api/tan/report/html")
    assert html.status_code == 200
    assert "Verificaciones" in html.text
    csv_body = client.get("/api/tan/report/csv")
    assert csv_body.status_code == 200
    assert "codigo" in csv_body.text


def test_report_requires_prior_design():
    import tan_service

    tan_service._last_reports = {}
    client = TestClient(app)
    missing = client.get("/api/tan/report/pdf")
    assert missing.status_code == 404
    bad = client.get("/api/tan/report/docx")
    assert bad.status_code == 400


def test_power_stage_fault_appears_in_project():
    store.reset()
    client = TestClient(app)
    tripped = client.post("/api/power-stage/command", json={"command": "inject_fault", "fault": "OVERCURRENT"})
    assert tripped.status_code == 200
    project = client.get("/api/project").json()
    assert project["links"]["bank_fault_recorded"] is True
    assert project["power_stage"]["fault"] == "OVERCURRENT"
