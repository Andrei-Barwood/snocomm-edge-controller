import pytest

from power_stage import FaultCode, PowerStageConfig, PowerStageController, PowerStageState


def advance_until(controller, target, attempts=100):
    for _ in range(attempts):
        snapshot = controller.tick(0.1)
        if snapshot["state"] == target.value:
            return snapshot
    raise AssertionError(f"Controller never reached {target.value}")


def test_complete_safe_startup_and_shutdown():
    controller = PowerStageController()
    controller.command("start")
    ready = advance_until(controller, PowerStageState.READY)

    assert ready["outputs"]["main_contactor"] is True
    assert ready["outputs"]["precharge_contactor"] is False
    assert ready["outputs"]["pwm_enabled"] is False

    running = controller.command("enable")
    assert running["state"] == PowerStageState.RUN.value
    assert running["outputs"]["gate_enable"] is True
    assert running["outputs"]["pwm_enabled"] is True

    stopped = controller.command("shutdown")
    assert stopped["state"] == PowerStageState.POWER_OFF.value
    assert stopped["outputs"]["main_contactor"] is False
    assert stopped["outputs"]["precharge_contactor"] is False
    assert stopped["outputs"]["gate_enable"] is False
    assert stopped["outputs"]["pwm_enabled"] is False


def test_estop_immediately_forces_safe_outputs_and_latches():
    controller = PowerStageController()
    controller.command("start")
    advance_until(controller, PowerStageState.READY)
    controller.command("enable")

    stopped = controller.command("estop")
    assert stopped["state"] == PowerStageState.ESTOP.value
    assert stopped["fault"] == FaultCode.ESTOP_ACTIVE.value
    assert stopped["outputs"]["main_contactor"] is False
    assert stopped["outputs"]["precharge_contactor"] is False
    assert stopped["outputs"]["gate_enable"] is False
    assert stopped["outputs"]["pwm_enabled"] is False

    with pytest.raises(ValueError, match="Libere"):
        controller.command("reset_fault")

    controller.command("release_estop")
    reset = controller.command("reset_fault")
    assert reset["state"] == PowerStageState.POWER_OFF.value
    assert reset["fault"] == FaultCode.NONE.value


def test_injected_overcurrent_is_latched():
    controller = PowerStageController()
    faulted = controller.command("inject_fault", FaultCode.OVERCURRENT.value)
    assert faulted["state"] == PowerStageState.FAULT_LATCHED.value
    assert faulted["fault"] == FaultCode.OVERCURRENT.value
    assert faulted["physical_outputs_available"] is False


def test_precharge_timeout_latches_fault():
    controller = PowerStageController(
        PowerStageConfig(precharge_timeout_s=0.5, precharge_tau_s=20.0)
    )
    controller.command("start")
    snapshot = advance_until(controller, PowerStageState.FAULT_LATCHED)
    assert snapshot["fault"] == FaultCode.PRECHARGE_TIMEOUT.value
    assert not any(snapshot["outputs"].values())


def test_pwm_cannot_start_before_ready():
    controller = PowerStageController()
    with pytest.raises(ValueError, match="READY"):
        controller.command("enable")
    controller.command("start")
    assert controller.snapshot()["state"] != PowerStageState.READY.value
    with pytest.raises(ValueError, match="READY"):
        controller.command("enable")


def test_physical_outputs_false_in_power_off_run_estop_and_fault():
    controller = PowerStageController()
    off = controller.snapshot()
    assert off["state"] == PowerStageState.POWER_OFF.value
    assert off["physical_outputs_available"] is False

    controller.command("start")
    advance_until(controller, PowerStageState.READY)
    running = controller.command("enable")
    assert running["state"] == PowerStageState.RUN.value
    assert running["physical_outputs_available"] is False
    assert running["outputs"]["pwm_enabled"] is True

    stopped = controller.command("estop")
    assert stopped["state"] == PowerStageState.ESTOP.value
    assert stopped["physical_outputs_available"] is False
    assert stopped["outputs"]["main_contactor"] is False
    assert stopped["outputs"]["precharge_contactor"] is False
    assert stopped["outputs"]["gate_enable"] is False
    assert stopped["outputs"]["pwm_enabled"] is False

    faulted = PowerStageController()
    snap = faulted.command("inject_fault", FaultCode.OVERCURRENT.value)
    assert snap["state"] == PowerStageState.FAULT_LATCHED.value
    assert snap["physical_outputs_available"] is False


def test_no_automatic_restart_after_overcurrent():
    controller = PowerStageController()
    controller.command("start")
    advance_until(controller, PowerStageState.READY)
    controller.command("enable")
    faulted = controller.command("inject_fault", FaultCode.OVERCURRENT.value)
    assert faulted["state"] == PowerStageState.FAULT_LATCHED.value
    assert faulted["fault"] == FaultCode.OVERCURRENT.value

    with pytest.raises(ValueError, match="POWER_OFF"):
        controller.command("start")
    with pytest.raises(ValueError, match="READY"):
        controller.command("enable")
    still = controller.snapshot()
    assert still["state"] == PowerStageState.FAULT_LATCHED.value
    assert still["fault"] == FaultCode.OVERCURRENT.value

    reset = controller.command("reset_fault")
    assert reset["state"] == PowerStageState.POWER_OFF.value
    controller.command("start")
    ready = advance_until(controller, PowerStageState.READY)
    assert ready["state"] == PowerStageState.READY.value


def test_precharge_reaches_90_percent_before_ready():
    controller = PowerStageController()
    controller.command("start")
    ratio = controller.config.precharge_target_ratio
    main_seen = False
    for _ in range(100):
        snap = controller.tick(0.1)
        source = snap["measurements"]["source_v"]
        vdc = snap["measurements"]["dc_bus_v"]
        if snap["outputs"]["main_contactor"] and not main_seen:
            assert vdc >= source * ratio
            main_seen = True
        if snap["state"] == PowerStageState.READY.value:
            assert main_seen
            assert vdc >= source * ratio
            return
    raise AssertionError("Controller never reached READY")


def test_inject_dc_overvoltage_and_overtemperature_latch():
    for code in (FaultCode.DC_OVERVOLTAGE, FaultCode.OVERTEMPERATURE):
        controller = PowerStageController()
        controller.command("start")
        advance_until(controller, PowerStageState.READY)
        controller.command("enable")
        snap = controller.command("inject_fault", code.value)
        assert snap["state"] == PowerStageState.FAULT_LATCHED.value
        assert snap["fault"] == code.value
        assert snap["physical_outputs_available"] is False
        assert snap["outputs"]["main_contactor"] is False
        assert snap["outputs"]["precharge_contactor"] is False
        assert snap["outputs"]["gate_enable"] is False
        assert snap["outputs"]["pwm_enabled"] is False
        with pytest.raises(ValueError, match="READY"):
            controller.command("enable")
        with pytest.raises(ValueError, match="POWER_OFF"):
            controller.command("start")


def test_hil_rating_matches_kps305d_24v():
    cfg = PowerStageConfig()
    assert cfg.nominal_bus_v == 24.0
    assert cfg.rated_current_a == 5.0
    assert cfg.rated_power_w == 120.0
    assert cfg.overvoltage_trip_v <= cfg.source_ceiling_v
    assert cfg.source_ceiling_v == 30.0
    controller = PowerStageController()
    snap = controller.snapshot()
    assert snap["measurements"]["source_v"] == 24.0
    assert snap["physical_outputs_available"] is False
