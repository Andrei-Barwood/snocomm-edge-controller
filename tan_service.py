"""Shared TAN-Telecom web API used by both controller launch modes."""

from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from project_store import store
from tan_telecom.export import REPORT_FORMATS, export_bundle
from tan_telecom.rules import run_design
from tan_telecom.validators import ValidationError, build_inputs

_last_reports: dict[str, Path] = {}
WEB_OUTPUT = Path("output") / "web"


class DesignRequest(BaseModel):
    potencia_kw: float = Field(gt=0, le=5000)
    num_racks: int = Field(ge=1, le=200)
    redundancia: Literal["N", "N+1", "2N"] = "N+1"
    ip_minimo: Literal[30, 31, 40, 41, 54, 55, 65, 66] = 54
    carga_armonica: bool = True
    sismico: bool = False


router = APIRouter(prefix="/api/tan", tags=["TAN-Telecom"])


@router.post("/design")
async def design_panel(payload: DesignRequest):
    """Validate inputs and return the complete IEC 61439 design result."""
    try:
        inputs = build_inputs(
            potencia_kw=payload.potencia_kw,
            num_racks=payload.num_racks,
            redundancia=payload.redundancia,
            ip_minimo=payload.ip_minimo,
            carga_armonica=payload.carga_armonica,
            sismico=payload.sismico,
            output=str(Path("output") / "web"),
        )
        result = run_design(inputs, version="1.0.0")
        snapshot = store.snapshot()
        enriched = store.update_tan(result.to_dict())
        extras = {
            "shared_project_id": enriched.get("shared_project_id"),
            "observed_harmonics": enriched.get("observed_harmonics"),
            "compensation_current_a": enriched.get("compensation_current_a"),
            "ahf_module_suggestion": enriched.get("ahf_module_suggestion"),
            "ric04_neutral_note": enriched.get("ric04_neutral_note"),
            "power_stage": snapshot.get("power_stage"),
        }
        result.warnings = list(enriched.get("warnings") or result.warnings)
        paths = export_bundle(result, WEB_OUTPUT, extras=extras)
        global _last_reports
        _last_reports = paths
        reports = {
            fmt: {
                "url": f"/api/tan/report/{fmt}",
                "filename": path.name,
                "bytes": path.stat().st_size,
            }
            for fmt, path in paths.items()
        }
        return {**enriched, "reports": reports}
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/reports")
async def list_reports():
    if not _last_reports:
        raise HTTPException(status_code=404, detail="Calcule un diseño para generar informes.")
    return {
        fmt: {
            "url": f"/api/tan/report/{fmt}",
            "filename": path.name,
            "bytes": path.stat().st_size,
            "media_type": REPORT_FORMATS[fmt][0],
        }
        for fmt, path in _last_reports.items()
    }


@router.get("/report/{fmt}")
async def download_report(fmt: str):
    key = fmt.lower().lstrip(".")
    if key not in REPORT_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado. Use: {', '.join(REPORT_FORMATS)}.",
        )
    path = _last_reports.get(key)
    if path is None or not path.exists():
        raise HTTPException(status_code=404, detail="Calcule un diseño para generar informes.")
    return FileResponse(
        path,
        media_type=REPORT_FORMATS[key][0],
        filename=path.name,
    )

