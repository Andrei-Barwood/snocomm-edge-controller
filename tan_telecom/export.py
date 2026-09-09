"""Paquete documental TAN en varios formatos."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .generators.excel_generator import generate_excel
from .generators.pdf_generator import generate_pdf
from .generators.text_generators import generate_bom_csv, generate_html, generate_markdown
from .models import ProjectResult

REPORT_FORMATS: dict[str, tuple[str, str]] = {
    "xlsx": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "_documentacion.xlsx",
    ),
    "pdf": ("application/pdf", "_resumen.pdf"),
    "json": ("application/json", "_config.json"),
    "md": ("text/markdown; charset=utf-8", "_memoria.md"),
    "html": ("text/html; charset=utf-8", "_informe.html"),
    "csv": ("text/csv; charset=utf-8", "_bom.csv"),
}


def export_bundle(
    result: ProjectResult,
    output_dir: Path,
    extras: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """Escribe Excel, PDF, JSON, Markdown, HTML y CSV de la BOM."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = result.project_id
    extras = extras or {}
    payload = {**result.to_dict(), **extras}
    paths = {
        "xlsx": output_dir / f"{stem}{REPORT_FORMATS['xlsx'][1]}",
        "pdf": output_dir / f"{stem}{REPORT_FORMATS['pdf'][1]}",
        "json": output_dir / f"{stem}{REPORT_FORMATS['json'][1]}",
        "md": output_dir / f"{stem}{REPORT_FORMATS['md'][1]}",
        "html": output_dir / f"{stem}{REPORT_FORMATS['html'][1]}",
        "csv": output_dir / f"{stem}{REPORT_FORMATS['csv'][1]}",
    }
    generate_excel(result, paths["xlsx"], extras=extras)
    generate_pdf(result, paths["pdf"], extras=extras)
    paths["json"].write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    generate_markdown(result, paths["md"], extras=extras)
    generate_html(result, paths["html"], extras=extras)
    generate_bom_csv(result, paths["csv"])
    return paths
