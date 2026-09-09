"""Deterministic state machine for the 24 V / 120 W HIL prototype.

Limits match the pañol source (wanptek KPS305D, 0–30 V / 0–5 A, 24.0 V work
point). This module has no GPIO, PWM, contactor, or gate-driver backend.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
import math
from threading import RLock
import time
from typing import Any


class PowerStageState(str, Enum):
    POWER_OFF = "POWER_OFF"
    SELF_TEST = "SELF_TEST"
    PRECHARGE = "PRECHARGE"
    READY = "READY"
    RUN = "RUN"
    FAULT_LATCHED = "FAULT_LATCHED"
    ESTOP = "ESTOP"


class FaultCode(str, Enum):
    NONE = "NONE"
    ESTOP_ACTIVE = "ESTOP_ACTIVE"
    OVERCURRENT = "OVERCURRENT"
    DC_OVERVOLTAGE = "DC_OVERVOLTAGE"
    DC_UNDERVOLTAGE = "DC_UNDERVOLTAGE"
    OVERTEMPERATURE = "OVERTEMPERATURE"
    SENSOR_FAULT = "SENSOR_FAULT"
    GATE_DRIVER_FAULT = "GATE_DRIVER_FAULT"
    PRECHARGE_TIMEOUT = "PRECHARGE_TIMEOUT"


@dataclass(frozen=True)
class PowerStageConfig:
    rated_power_w: float = 120.0
    nominal_bus_v: float = 24.0
    rated_current_a: float = 5.0
    overcurrent_trip_a: float = 5.5
    overvoltage_trip_v: float = 29.0
    undervoltage_trip_v: float = 18.0
    source_ceiling_v: float = 30.0
    overtemperature_trip_c: float = 85.0
    precharge_target_ratio: float = 0.90
    precharge_timeout_s: float = 5.0
    precharge_tau_s: float = 0.65
    discharge_tau_s: float = 2.5
    self_test_duration_s: float = 0.35
    main_contactor_settle_s: float = 0.12


class PowerStageController:
    """Fail-safe HIL controller with latched faults and a precharge sequence."""

    def __init__(self, config: PowerStageConfig | None = None) -> None:
        self.config = config or PowerStageConfig()
        self._lock = RLock()
        self._now = time.monotonic()
        self._state_entered = self._now
        self._main_closed_at: float | None = None
        self.state = PowerStageState.POWER_OFF
        self.fault = FaultCode.NONE
        self.fault_message = ""
        self.dc_bus_v = 0.0
        self.source_v = self.config.nominal_bus_v
        self.phase_current_a = 0.0
        self.temperature_c = 27.0
        self.sensor_ok = True
        self.gate_driver_ready = True
        self.estop_active = False
        self.main_contactor = False
        self.precharge_contactor = False
        self.gate_enable = False
        self.pwm_enabled = False
        self.events: list[dict[str, str]] = []
        self._record("Sistema HIL inicializado; salidas físicas no disponibles.")

    def _record(self, message: str) -> None:
        self.events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "state": self.state.value,
            "message": message,
        })
        self.events = self.events[-50:]

    def _enter(self, state: PowerStageState, message: str) -> None:
        self.state = state
        self._state_entered = self._now
        self._record(message)

    def _outputs_safe(self, open_contactors: bool = True) -> None:
        self.pwm_enabled = False
        self.gate_enable = False
        if open_contactors:
            self.main_contactor = False
            self.precharge_contactor = False
            self._main_closed_at = None

    def _trip(self, fault: FaultCode, message: str, estop: bool = False) -> None:
        if self.state in {PowerStageState.FAULT_LATCHED, PowerStageState.ESTOP}:
            return
        self.fault = fault
        self.fault_message = message
        self._outputs_safe(open_contactors=True)
        self._enter(PowerStageState.ESTOP if estop else PowerStageState.FAULT_LATCHED, message)

    def _safe_to_start(self) -> bool:
        return (
            not self.estop_active
            and self.sensor_ok
            and self.gate_driver_ready
            and self.temperature_c < self.config.overtemperature_trip_c
            and self.source_v <= self.config.overvoltage_trip_v
        )

    def _update_simulation(self, dt: float) -> None:
        if self.main_contactor:
            self.dc_bus_v += (self.source_v - self.dc_bus_v) * (1.0 - math.exp(-dt / 0.04))
        elif self.precharge_contactor:
            self.dc_bus_v += (self.source_v - self.dc_bus_v) * (
                1.0 - math.exp(-dt / self.config.precharge_tau_s)
            )
        else:
            self.dc_bus_v *= math.exp(-dt / self.config.discharge_tau_s)

        if self.state == PowerStageState.RUN:
            self.phase_current_a = min(self.config.rated_current_a * 0.72, self.phase_current_a + dt * 7.0)
            self.temperature_c = min(52.0, self.temperature_c + dt * 0.45)
        else:
            self.phase_current_a = max(0.0, self.phase_current_a - dt * 10.0)
            self.temperature_c = max(27.0, self.temperature_c - dt * 0.15)

    def _evaluate_protections(self) -> None:
        if self.estop_active:
            self._trip(FaultCode.ESTOP_ACTIVE, "Parada de emergencia activada.", estop=True)
        elif not self.sensor_ok:
            self._trip(FaultCode.SENSOR_FAULT, "Se perdió una medición crítica.")
        elif not self.gate_driver_ready:
            self._trip(FaultCode.GATE_DRIVER_FAULT, "El driver de compuerta reportó una falla.")
        elif self.phase_current_a >= self.config.overcurrent_trip_a:
            self._trip(FaultCode.OVERCURRENT, "Protección de sobrecorriente activada.")
        elif self.dc_bus_v >= self.config.overvoltage_trip_v:
            self._trip(FaultCode.DC_OVERVOLTAGE, "Sobretensión detectada en el DC-link.")
        elif self.temperature_c >= self.config.overtemperature_trip_c:
            self._trip(FaultCode.OVERTEMPERATURE, "Temperatura máxima superada.")
        elif self.state == PowerStageState.RUN and self.dc_bus_v <= self.config.undervoltage_trip_v:
            self._trip(FaultCode.DC_UNDERVOLTAGE, "El DC-link cayó bajo el límite operativo.")

    def _advance_state_machine(self) -> None:
        elapsed = self._now - self._state_entered
        if self.state == PowerStageState.SELF_TEST and elapsed >= self.config.self_test_duration_s:
            if not self._safe_to_start():
                self._trip(FaultCode.SENSOR_FAULT, "La autoprueba no confirmó condiciones seguras.")
                return
            self.precharge_contactor = True
            self._enter(PowerStageState.PRECHARGE, "Autoprueba correcta; precarga iniciada.")

        if self.state == PowerStageState.PRECHARGE:
            elapsed = self._now - self._state_entered
            target = self.source_v * self.config.precharge_target_ratio
            if elapsed >= self.config.precharge_timeout_s and self.dc_bus_v < target:
                self._trip(FaultCode.PRECHARGE_TIMEOUT, "El DC-link no alcanzó el umbral de precarga.")
            elif self.dc_bus_v >= target and not self.main_contactor:
                self.main_contactor = True
                self._main_closed_at = self._now
                self._record("Umbral de precarga alcanzado; contactor principal cerrado.")
            elif self.main_contactor and self._main_closed_at is not None:
                if self._now - self._main_closed_at >= self.config.main_contactor_settle_s:
                    self.precharge_contactor = False
                    self._enter(PowerStageState.READY, "Precarga finalizada; etapa lista para habilitación.")

    def tick(self, seconds: float | None = None) -> dict[str, Any]:
        """Advance the HIL plant and return a serializable snapshot."""
        with self._lock:
            previous = self._now
            self._now = previous + seconds if seconds is not None else time.monotonic()
            dt = max(0.0, min(self._now - previous, 0.25))
            self._update_simulation(dt)
            self._evaluate_protections()
            self._advance_state_machine()
            return self.snapshot()

    def command(self, name: str, fault: str | None = None) -> dict[str, Any]:
        with self._lock:
            self.tick()
            if name == "start":
                if self.state != PowerStageState.POWER_OFF:
                    raise ValueError("La secuencia sólo puede comenzar desde POWER_OFF.")
                if not self._safe_to_start():
                    raise ValueError("Los interlocks no permiten iniciar la secuencia.")
                self.fault = FaultCode.NONE
                self.fault_message = ""
                self._enter(PowerStageState.SELF_TEST, "Secuencia de arranque solicitada.")
            elif name == "enable":
                if self.state != PowerStageState.READY:
                    raise ValueError("El PWM sólo puede habilitarse desde READY.")
                self.gate_enable = True
                self.pwm_enabled = True
                self._enter(PowerStageState.RUN, "PWM HIL habilitado; etapa en operación simulada.")
            elif name == "shutdown":
                self._outputs_safe(open_contactors=True)
                self._enter(PowerStageState.POWER_OFF, "Parada controlada completada.")
            elif name == "estop":
                self.estop_active = True
                self._trip(FaultCode.ESTOP_ACTIVE, "Parada de emergencia activada por el operador.", estop=True)
            elif name == "release_estop":
                self.estop_active = False
                self._record("Parada de emergencia liberada; se requiere reset manual.")
            elif name == "reset_fault":
                if self.state not in {PowerStageState.FAULT_LATCHED, PowerStageState.ESTOP}:
                    raise ValueError("No existe una falla enclavada para rearmar.")
                if self.estop_active:
                    raise ValueError("Libere la parada de emergencia antes de rearmar.")
                self.sensor_ok = True
                self.gate_driver_ready = True
                self.phase_current_a = 0.0
                self.temperature_c = min(self.temperature_c, 40.0)
                self.source_v = self.config.nominal_bus_v
                self.fault = FaultCode.NONE
                self.fault_message = ""
                self._outputs_safe(open_contactors=True)
                self._enter(PowerStageState.POWER_OFF, "Falla rearmada; sistema en estado seguro.")
            elif name == "inject_fault":
                try:
                    injected = FaultCode(fault or "")
                except ValueError as exc:
                    raise ValueError("Código de falla HIL inválido.") from exc
                if injected == FaultCode.NONE:
                    raise ValueError("Seleccione una falla distinta de NONE.")
                self._trip(injected, f"Falla HIL inyectada: {injected.value}.", estop=injected == FaultCode.ESTOP_ACTIVE)
                if injected == FaultCode.ESTOP_ACTIVE:
                    self.estop_active = True
            else:
                raise ValueError("Comando HIL no reconocido.")
            return self.snapshot()

    def snapshot(self) -> dict[str, Any]:
        target = max(self.source_v * self.config.precharge_target_ratio, 0.1)
        progress = min(100.0, (self.dc_bus_v / target) * 100.0)
        return {
            "mode": "HIL_SIMULATION_ONLY",
            "physical_outputs_available": False,
            "state": self.state.value,
            "fault": self.fault.value,
            "fault_message": self.fault_message,
            "measurements": {
                "dc_bus_v": round(self.dc_bus_v, 2),
                "source_v": round(self.source_v, 2),
                "phase_current_a": round(self.phase_current_a, 2),
                "temperature_c": round(self.temperature_c, 1),
                "precharge_percent": round(progress, 1),
            },
            "outputs": {
                "main_contactor": self.main_contactor,
                "precharge_contactor": self.precharge_contactor,
                "gate_enable": self.gate_enable,
                "pwm_enabled": self.pwm_enabled,
            },
            "interlocks": {
                "estop_ok": not self.estop_active,
                "sensor_ok": self.sensor_ok,
                "gate_driver_ready": self.gate_driver_ready,
            },
            "limits": asdict(self.config),
            "events": list(reversed(self.events[-12:])),
        }
