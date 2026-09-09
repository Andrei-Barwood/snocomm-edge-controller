"""Camino de defensa del TPA: DSP, runtime HIL, banco 24 V, SIL, TAN small."""

from __future__ import annotations

from fastapi.testclient import TestClient

from dsp.core import BlockDspController
from dsp.patterns import generate_pattern_batch, pattern_catalog
from hil_app import app
from power_stage import PowerStageController, PowerStageState
from tan_telecom.models import ProjectInputs, Redundancia
from tan_telecom.rules import run_design

FS = 12_800
BATCH = 128


def test_combined_it_pattern_produces_thdi():
    spec = pattern_catalog()["combined_it"]
    dsp = BlockDspController(
        sampling_rate=FS,
        nominal_frequency=50.0,
        kp=0.5,
        ki=5.0,
        max_current_rms=200.0,
        voltage_ln_rms=230.0,
    )
    t0 = 0.0
    freq = spec.frequency_hz
    result = None
    for _ in range(int(0.60 * FS / BATCH)):
        batch, freq, t0 = generate_pattern_batch(spec, t0, FS, BATCH, current_freq=freq)
        result = dsp.process(batch)
    assert result is not None
    assert result.thdi > 0


def test_runtime_is_hil_simulation():
    client = TestClient(app)
    runtime = client.get("/api/runtime").json()
    assert runtime["launch_mode"] == "hil"
    assert runtime["hardware"] == "hil_simulation"


def test_bench_package_voltage_class_is_24():
    client = TestClient(app)
    pack = client.get("/api/bench/package").json()
    assert "24" in pack["voltage_class"]


def test_physical_outputs_false_in_run():
    controller = PowerStageController()
    controller.command("start")
    ready = None
    for _ in range(100):
        snap = controller.tick(0.1)
        if snap["state"] == PowerStageState.READY.value:
            ready = snap
            break
    assert ready is not None, "el HIL no alcanzó READY"
    running = controller.command("enable")
    assert running["state"] == PowerStageState.RUN.value
    assert running["physical_outputs_available"] is False


def test_tan_small_example_does_not_explode():
    inputs = ProjectInputs(
        45.0, 4, Redundancia.N, ip_minimo=54, example_name="small"
    )
    result = run_design(inputs)
    assert result.project_id
    assert result.electrical.in_seleccion_a > 0
    assert result.enclosure.codigo
    assert result.verifications
