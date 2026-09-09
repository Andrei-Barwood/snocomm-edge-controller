"""Proyecto común y enriquecimiento TAN con THDi observado."""

from __future__ import annotations

from project_store import ProjectStore, compensation_current_a, suggest_ahf_module
from bench_package import bench_package


def test_compensation_current_and_module():
    assert compensation_current_a(3.0, 4.0, 12.0) == 13.0
    assert "50 A" in suggest_ahf_module(20.0)
    assert "100 A" in suggest_ahf_module(80.0)


def test_tan_consumes_monitor_thdi():
    store = ProjectStore()
    store.configure("industrial", "simulation", "hil_simulation", "combined_it")
    store.update_monitor(
        {
            "thdi": 22.9,
            "thdi_method": "Ih(3+5+7) / I1 · 100",
            "i1_rms": 70.7,
            "h3_rms": 14.1,
            "h5_rms": 7.1,
            "h7_rms": 3.5,
            "in_rms": 42.4,
            "disclaimer": "académico",
        }
    )
    merged = store.update_tan(
        {
            "project_id": "TT-M-TEST",
            "electrical": {"in_seleccion_a": 250},
            "separation": {"forma": "3b"},
            "enclosure": {"codigo": "XL3-800"},
            "warnings": [],
        }
    )
    assert merged["shared_project_id"] == store.snapshot()["project_id"]
    assert merged["compensation_current_a"] == 16.17
    assert merged["observed_harmonics"]["thdi"] == 22.9
    assert any("THDi observado" in item for item in merged["warnings"])
    snap = store.snapshot()
    assert snap["links"]["thdi_feeds_tan"] is True
    assert snap["links"]["dsp_commands_bank"] is False


def test_bank_fault_is_recorded_once_per_change():
    store = ProjectStore()
    store.update_power_stage({"state": "RUN", "fault": "NONE", "fault_message": ""})
    store.update_power_stage(
        {"state": "FAULT_LATCHED", "fault": "OVERCURRENT", "fault_message": "trip"}
    )
    store.update_power_stage(
        {"state": "FAULT_LATCHED", "fault": "OVERCURRENT", "fault_message": "trip"}
    )
    faults = [row for row in store.snapshot()["trail"] if "OVERCURRENT" in row["message"]]
    assert len(faults) == 1


def test_bench_package_has_acceptance_and_unifilar():
    pack = bench_package()
    assert pack["voltage_class"].startswith("24 V")
    assert "48" not in pack["voltage_class"]
    assert len(pack["unifilar"]) >= 6
    assert {item["id"] for item in pack["acceptance"]} >= {"A1", "A2", "A3"}
    assert pack["panol"] == "Pañol CFT Paillaco"
    assert pack["inventory"].endswith("INVENTARIO_PANOL_CFT_PAILLACO.md")
    usable = [row["item"] for row in pack["cft_bom"] if row.get("status") == "USABLE EN TPA"]
    assert any("KPS305D" in item for item in usable)
    assert any("GA1102CAL" in item for item in usable)
