"""API de la calculadora comparativa y del marco legal."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from calculator.engine import analyze, list_templates
from calculator.examples.catalog import CATALOG, example_path
from calculator.legal import LEGAL
from calculator.pdf_report import render_pdf
from calculator.stats import summarize_csv

router = APIRouter(prefix="/api/calculator", tags=["Calculadora"])
OUTPUT = Path("output") / "calculator"
_last: dict[str, Path] = {}


def _decode(raw: bytes) -> str:
    if len(raw) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="El CSV supera 5 MiB.")
    return raw.decode("utf-8", errors="replace")


async def _optional_csv(upload: UploadFile | None) -> tuple[str | None, str]:
    if upload is None or not upload.filename:
        return None, ""
    raw = await upload.read()
    if not raw:
        return None, upload.filename
    return _decode(raw), upload.filename


@router.get("/templates")
async def templates():
    return {"templates": list_templates(), "count": 24, "notice": LEGAL["short_notice"]}


@router.get("/legal")
async def legal():
    return LEGAL


@router.get("/examples")
async def list_examples():
    return {
        "examples": [
            {**item, "url": f"/api/calculator/examples/{item['file']}"}
            for item in CATALOG
        ]
    }


@router.get("/examples/{filename}")
async def download_example(filename: str):
    allowed = {item["file"] for item in CATALOG}
    if filename not in allowed:
        raise HTTPException(status_code=404, detail="No hay un CSV de demo con ese nombre.")
    try:
        path = example_path(filename)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(path, media_type="text/csv", filename=filename)


@router.post("/preview")
async def preview(file: UploadFile = File(...)):
    text, name = await _optional_csv(file)
    if not text:
        raise HTTPException(status_code=422, detail="Suba un CSV con encabezado y datos.")
    try:
        return summarize_csv(text, name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/analyze")
async def run_analysis(
    template_id: str = Form(...),
    params: str = Form("{}"),
    csv_before: UploadFile | None = File(None),
    csv_after: UploadFile | None = File(None),
):
    try:
        payload: dict[str, Any] = json.loads(params or "{}")
        if not isinstance(payload, dict):
            raise ValueError("params debe ser un objeto JSON")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Parámetros inválidos: {exc}") from exc
    before_text, before_name = await _optional_csv(csv_before)
    after_text, after_name = await _optional_csv(csv_after)
    if not before_text and not after_text:
        raise HTTPException(
            status_code=422,
            detail="Suba al menos un CSV de osciloscopio (anterior, nuevo, o ambos).",
        )
    try:
        result = analyze(template_id, payload, before_text, before_name, after_text, after_name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Plantilla desconocida: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    pdf_path = render_pdf(result, OUTPUT / f"{result['run_id']}.pdf")
    _last[result["run_id"]] = pdf_path
    result["pdf"] = {
        "url": f"/api/calculator/report/{result['run_id']}.pdf",
        "filename": pdf_path.name,
        "bytes": pdf_path.stat().st_size,
    }
    return result


@router.get("/report/{run_id}.pdf")
async def download_pdf(run_id: str):
    path = _last.get(run_id) or (OUTPUT / f"{run_id}.pdf")
    if not Path(path).is_file():
        raise HTTPException(status_code=404, detail="No hay informe para ese identificador.")
    return FileResponse(path, media_type="application/pdf", filename=Path(path).name)
