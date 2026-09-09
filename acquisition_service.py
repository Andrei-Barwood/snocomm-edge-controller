"""API de campañas importadas (CSV de osciloscopio y JSON de central)."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from acquisition.parser import parse_csv, parse_json_campaign, suggest_mapping
from acquisition.pipeline import example_scope_csv, process_campaign
from project_store import store

router = APIRouter(prefix="/api/acquisition", tags=["Adquisición importada"])

_session: dict[str, Any] = {
    "previous_acquisition": None,
    "last": None,
}


class LiveCampaign(BaseModel):
    source: str = "meter"
    circuit: str = "ac"
    fs: float | None = Field(default=None, gt=1)
    mapping: dict[str, str] | None = None
    channels: dict[str, list[float]] | None = None
    registers: dict[str, float] | None = None
    current_scale: float = 1.0
    voltage_scale: float = 1.0


def _apply_import(result, filename: str) -> dict[str, Any]:
    runtime = store.runtime()
    if runtime["acquisition"] != "imported":
        _session["previous_acquisition"] = runtime["acquisition"]
    store.configure(
        runtime["launch_mode"],
        "imported",
        runtime["hardware"],
        filename,
    )
    telemetry = result.telemetry
    store.update_monitor(telemetry)
    payload = {
        "telemetry": telemetry,
        "meta": result.meta,
        "warnings": result.warnings,
    }
    _session["last"] = payload
    return payload


@router.get("/example.csv")
async def download_example_csv():
    return PlainTextResponse(
        example_scope_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="snocomm_ejemplo_scope.csv"'},
    )


@router.get("/last")
async def last_import():
    if not _session["last"]:
        raise HTTPException(status_code=404, detail="No hay una campaña importada.")
    return _session["last"]


@router.post("/clear")
async def clear_import():
    previous = _session["previous_acquisition"] or "none"
    runtime = store.runtime()
    store.configure(runtime["launch_mode"], previous, runtime["hardware"])
    _session["last"] = None
    _session["previous_acquisition"] = None
    return store.runtime()


@router.post("/preview")
async def preview_file(file: UploadFile = File(...)):
    raw = (await file.read()).decode("utf-8", errors="replace")
    name = file.filename or "captura"
    try:
        if name.lower().endswith(".json"):
            table, registers = parse_json_campaign(json.loads(raw))
            headers = table.headers if table else list(registers)
            mapping = table.mapping if table else {}
            preview = table.preview() if table else [registers]
            warnings = table.warnings if table else ["Solo registros."]
        else:
            table = parse_csv(raw)
            headers = table.headers
            mapping = table.mapping
            preview = table.preview()
            warnings = table.warnings
            registers = {}
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "filename": name,
        "headers": headers,
        "suggested_mapping": mapping,
        "preview": preview,
        "registers": registers,
        "warnings": warnings,
        "available_channels": ["time", "ia", "ib", "ic", "in", "va", "vb", "vc"],
    }


@router.post("/import")
async def import_file(
    file: UploadFile = File(...),
    mapping: str | None = Form(default=None),
    fs: float | None = Form(default=None),
    current_scale: float = Form(default=1.0),
    voltage_scale: float = Form(default=1.0),
):
    raw = (await file.read()).decode("utf-8", errors="replace")
    name = file.filename or "captura"
    user_map = None
    if mapping:
        try:
            user_map = json.loads(mapping)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=422, detail="mapping debe ser JSON.") from exc
    try:
        if name.lower().endswith(".json") or raw.lstrip().startswith("{"):
            table, registers = parse_json_campaign(json.loads(raw))
            if user_map and table:
                table.mapping.update(user_map)
        else:
            table = parse_csv(raw, mapping=user_map)
            registers = {}
        result = process_campaign(
            table,
            registers,
            fs=fs,
            current_scale=current_scale,
            voltage_scale=voltage_scale,
            filename=name,
        )
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _apply_import(result, name)


@router.post("/live")
async def import_live(payload: LiveCampaign):
    body = payload.model_dump()
    if payload.channels:
        body.update(payload.channels)
    try:
        table, registers = parse_json_campaign(body)
        if payload.registers:
            registers.update(payload.registers)
        result = process_campaign(
            table,
            registers,
            fs=payload.fs,
            current_scale=payload.current_scale,
            voltage_scale=payload.voltage_scale,
            filename=payload.source,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _apply_import(result, payload.source)
