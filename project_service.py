"""API del proyecto común, estado de ejecución y paquete del banco 24 V."""

from __future__ import annotations

from fastapi import APIRouter

from bench_package import bench_package
from project_store import store

router = APIRouter(tags=["Proyecto común"])


@router.get("/api/runtime")
async def runtime_status():
    return store.runtime()


@router.get("/api/project")
async def project_snapshot():
    return store.snapshot()


@router.post("/api/project/reset")
async def reset_project():
    return store.reset()


@router.get("/api/bench/package")
async def physical_bench_package():
    return bench_package()
