"""Proyecto común en memoria: Monitor AHF, TAN y Banco 24 V comparten un id."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
from threading import RLock
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _project_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"SNO-{stamp}"


def compensation_current_a(h3_rms: float, h5_rms: float, h7_rms: float) -> float:
    return math.sqrt(h3_rms * h3_rms + h5_rms * h5_rms + h7_rms * h7_rms)


def suggest_ahf_module(i_comp_a: float) -> str:
    if i_comp_a <= 50.0:
        return "Módulo académico de referencia 50 A (no es un rating de producto)."
    if i_comp_a <= 100.0:
        return "Módulo académico de referencia 100 A, o 2 × 50 A en paralelo."
    modules = max(2, math.ceil(i_comp_a / 100.0))
    return f"Referencia académica: {modules} módulos de 100 A en paralelo (requiere medición)."


@dataclass
class SharedProject:
    project_id: str
    created_at: str
    launch_mode: str = "hil"
    acquisition: str = "none"
    hardware: str = "not_connected"
    server: str = "running"
    telemetry_live: bool = False
    pattern_name: str | None = None
    tan: dict[str, Any] | None = None
    monitor: dict[str, Any] | None = None
    power_stage: dict[str, Any] | None = None
    trail: list[dict[str, str]] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        monitor = self.monitor or {}
        thdi = monitor.get("thdi")
        i_comp = monitor.get("i_comp_rms")
        if i_comp is None and monitor:
            i_comp = compensation_current_a(
                float(monitor.get("h3_rms") or 0.0),
                float(monitor.get("h5_rms") or 0.0),
                float(monitor.get("h7_rms") or 0.0),
            )
        bank = self.power_stage or {}
        return {
            "project_id": self.project_id,
            "created_at": self.created_at,
            "server": self.server,
            "launch_mode": self.launch_mode,
            "acquisition": self.acquisition,
            "hardware": self.hardware,
            "telemetry_live": self.telemetry_live,
            "pattern_name": self.pattern_name,
            "tan": self.tan,
            "monitor": self.monitor,
            "power_stage": {
                "state": bank.get("state"),
                "fault": bank.get("fault"),
                "fault_message": bank.get("fault_message"),
                "physical_outputs_available": bank.get("physical_outputs_available", False),
            }
            if bank
            else None,
            "links": {
                "thdi_feeds_tan": thdi is not None and self.tan is not None,
                "observed_thdi": thdi,
                "tan_compensation_current_a": None
                if self.tan is None
                else self.tan.get("compensation_current_a"),
                "observed_compensation_current_a": i_comp,
                "dsp_commands_bank": False,
                "bank_fault_recorded": bool(bank.get("fault") and bank.get("fault") != "NONE"),
            },
            "trail": list(self.trail[-20:]),
        }


class ProjectStore:
    """Estado de un único proyecto de titulación por proceso servidor."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._project = SharedProject(project_id=_project_id(), created_at=_now())

    def configure(self, launch_mode: str, acquisition: str, hardware: str, pattern_name: str | None = None) -> None:
        with self._lock:
            self._project.launch_mode = launch_mode
            self._project.acquisition = acquisition
            self._project.hardware = hardware
            self._project.pattern_name = pattern_name
            self._record("runtime", f"Modo {launch_mode}; adquisición {acquisition}; hardware {hardware}.")

    def reset(self) -> dict[str, Any]:
        with self._lock:
            mode = self._project.launch_mode
            acq = self._project.acquisition
            hw = self._project.hardware
            pattern = self._project.pattern_name
            self._project = SharedProject(
                project_id=_project_id(),
                created_at=_now(),
                launch_mode=mode,
                acquisition=acq,
                hardware=hw,
                pattern_name=pattern,
            )
            self._record("runtime", "Proyecto común reiniciado.")
            return self._project.snapshot()

    def runtime(self) -> dict[str, Any]:
        with self._lock:
            p = self._project
            labels = {
                "simulation": "Señal patrón simulada",
                "none": "Sin productor DSP",
                "hardware_placeholder": "ADC marcador (ceros)",
                "imported": "Campaña importada (CSV/JSON)",
            }
            hw_labels = {
                "not_connected": "Sin etapa física",
                "hil_simulation": "Banco SIL, sin salidas",
            }
            return {
                "server": "running",
                "launch_mode": p.launch_mode,
                "acquisition": p.acquisition,
                "acquisition_label": labels.get(p.acquisition, p.acquisition),
                "hardware": p.hardware,
                "hardware_label": hw_labels.get(p.hardware, p.hardware),
                "telemetry_live": p.telemetry_live,
                "project_id": p.project_id,
                "pattern_name": p.pattern_name,
            }

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return self._project.snapshot()

    def update_monitor(self, telemetry: dict[str, Any]) -> None:
        with self._lock:
            compact = {
                "frame_count": telemetry.get("frame_count"),
                "freq_est": telemetry.get("freq_est"),
                "thdi": telemetry.get("thdi"),
                "thdi_method": telemetry.get("thdi_method"),
                "i1_rms": telemetry.get("i1_rms"),
                "h3_rms": telemetry.get("h3_rms"),
                "h5_rms": telemetry.get("h5_rms"),
                "h7_rms": telemetry.get("h7_rms"),
                "in_rms": telemetry.get("in_rms"),
                "i_comp_rms": telemetry.get("i_comp_rms"),
                "is_saturated": telemetry.get("is_saturated"),
                "pll_source": telemetry.get("pll_source"),
                "disclaimer": telemetry.get("disclaimer"),
            }
            first = self._project.monitor is None
            was_sat = bool((self._project.monitor or {}).get("is_saturated"))
            self._project.monitor = compact
            self._project.telemetry_live = True
            if first:
                self._record("monitor", "Primera trama DSP recibida en el proyecto común.")
            if compact.get("is_saturated") and not was_sat:
                self._record("monitor", "Referencia de compensación saturada (límite de corriente).")

    def update_tan(self, design: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            monitor = self._project.monitor or {}
            h3 = float(monitor.get("h3_rms") or 0.0)
            h5 = float(monitor.get("h5_rms") or 0.0)
            h7 = float(monitor.get("h7_rms") or 0.0)
            i_comp = compensation_current_a(h3, h5, h7) if monitor else None
            thdi = monitor.get("thdi")
            extra = {
                "shared_project_id": self._project.project_id,
                "observed_harmonics": None
                if not monitor
                else {
                    "thdi": thdi,
                    "thdi_method": monitor.get("thdi_method"),
                    "i1_rms": monitor.get("i1_rms"),
                    "h3_rms": h3,
                    "h5_rms": h5,
                    "h7_rms": h7,
                    "in_rms": monitor.get("in_rms"),
                    "disclaimer": monitor.get("disclaimer"),
                },
                "compensation_current_a": None if i_comp is None else round(i_comp, 2),
                "ahf_module_suggestion": None if i_comp is None else suggest_ahf_module(i_comp),
                "ric04_neutral_note": (
                    "RIC 04 p.5.3: con cargas no lineales el neutro debe ser al menos "
                    "50 % mayor que las fases, salvo excepción literal de filtro en la carga."
                ),
            }
            warnings = list(design.get("warnings") or [])
            if thdi is not None:
                warnings.append(
                    f"THDi observado en el monitor ({float(thdi):.1f} %) alimenta este "
                    "prediseño como evidencia académica, no como medición IEC/SEC."
                )
            if i_comp:
                warnings.append(
                    f"Corriente de compensación observada ≈ {i_comp:.1f} A RMS "
                    f"({extra['ahf_module_suggestion']})."
                )
            merged = {**design, **extra, "warnings": warnings}
            self._project.tan = {
                "project_id": design.get("project_id"),
                "shared_project_id": self._project.project_id,
                "in_seleccion_a": (design.get("electrical") or {}).get("in_seleccion_a"),
                "forma": (design.get("separation") or {}).get("forma"),
                "enclosure": (design.get("enclosure") or {}).get("codigo"),
                "compensation_current_a": extra["compensation_current_a"],
                "observed_thdi": thdi,
            }
            self._record(
                "tan",
                f"Prediseño {design.get('project_id')} asociado al proyecto {self._project.project_id}.",
            )
            return merged

    def update_power_stage(self, snapshot: dict[str, Any]) -> None:
        with self._lock:
            previous = self._project.power_stage or {}
            compact = {
                "state": snapshot.get("state"),
                "fault": snapshot.get("fault"),
                "fault_message": snapshot.get("fault_message"),
                "physical_outputs_available": snapshot.get("physical_outputs_available", False),
            }
            self._project.power_stage = compact
            if compact["state"] != previous.get("state"):
                self._record("banco", f"Estado del banco: {compact['state']}.")
            if compact["fault"] not in {None, "NONE"} and compact["fault"] != previous.get("fault"):
                self._record("banco", f"Falla enclavada: {compact['fault']} — {compact['fault_message']}")

    def _record(self, source: str, message: str) -> None:
        self._project.trail.append(
            {"timestamp": _now(), "source": source, "message": message}
        )
        self._project.trail = self._project.trail[-50:]


store = ProjectStore()
