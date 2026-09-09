"""FastAPI adapter for the simulation-only 24 V power-stage controller."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from power_stage import PowerStageController
from project_store import store


class PowerStageCommand(BaseModel):
    command: str
    fault: Optional[str] = None


runtime = PowerStageController()
router = APIRouter(prefix="/api/power-stage", tags=["24 V HIL power stage"])


@router.get("/status")
async def power_stage_status():
    snapshot = runtime.tick()
    store.update_power_stage(snapshot)
    return snapshot


@router.post("/command")
async def power_stage_command(payload: PowerStageCommand):
    try:
        snapshot = runtime.command(payload.command, payload.fault)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    store.update_power_stage(snapshot)
    return snapshot
