"""
Interfaz de línea de comandos profesional (Typer + Rich) para TAN-Telecom.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import box

from .export import export_bundle
from .models import ProjectInputs, ProjectResult
from .rules import run_design
from .validators import (
    ValidationError,
    build_inputs,
    validate_example_name,
)

__app_name__ = "TAN-Telecom"
__version__ = "1.0.0"

console = Console()
err_console = Console(stderr=True)

app = typer.Typer(
    name="tan-telecom",
    help=(
        "TAN-Telecom: diseño paramétrico de tableros TAN (IEC 61439) "
        "para nodos de telecomunicaciones e infraestructura informática."
    ),
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

EXAMPLES: dict[str, dict] = {
    "small": {
        "potencia_kw": 45.0,
        "num_racks": 4,
        "redundancia": "N",
        "ip_minimo": 54,
        "carga_armonica": False,
        "sismico": False,
    },
    "medium": {
        "potencia_kw": 120.0,
        "num_racks": 8,
        "redundancia": "N+1",
        "ip_minimo": 54,
        "carga_armonica": True,
        "sismico": False,
    },
    "large": {
        "potencia_kw": 350.0,
        "num_racks": 16,
        "redundancia": "2N",
        "ip_minimo": 55,
        "carga_armonica": True,
        "sismico": True,
    },
}


def _print_banner() -> None:
    console.print(
        Panel.fit(
            f"[bold cyan]{__app_name__}[/] [white]v{__version__}[/]\n"
            "[dim]Tableros TAN · IEC 61439-1/2 · Nodos de telecomunicaciones[/]",
            border_style="cyan",
        )
    )


def _print_summary(result: ProjectResult, verbose: bool = False) -> None:
    table = Table(
        title="Resumen de diseño",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=False,
    )
    table.add_column("Parámetro", style="bold")
    table.add_column("Valor")
    table.add_row("Project ID", result.project_id)
    table.add_row("Familia", result.separation.familia_tan)
    table.add_row("In base / diseño / selección",
                  f"{result.electrical.in_base_a} / "
                  f"{result.electrical.in_diseno_a} / "
                  f"{result.electrical.in_seleccion_a} A")
    table.add_row("Icc / Icw",
                  f"{result.electrical.icc_estimada_ka} / "
                  f"{result.electrical.icw_requerida_ka} kA")
    table.add_row("RDF", str(result.electrical.rdf))
    table.add_row(
        "ΔT estimado",
        f"{result.electrical.delta_t_estimado_c} °C "
        f"({'OK' if result.electrical.calentamiento_ok else 'REVISAR'})",
    )
    table.add_row("Envolvente", f"{result.enclosure.nombre} (IP{result.enclosure.ip_seleccionado})")
    table.add_row("Forma de separación", result.separation.forma.value)
    table.add_row("Criticidad", result.separation.criticidad)
    console.print(table)

    if result.warnings:
        for w in result.warnings:
            console.print(f"[bold yellow]⚠[/] {w}")

    if verbose:
        console.print("\n[bold]Justificación envolvente[/]")
        for line in result.enclosure.justificacion:
            console.print(f"  • {line}")
        console.print("\n[bold]Justificación forma[/]")
        for line in result.separation.justificacion:
            console.print(f"  • {line}")
        console.print("\n[bold]Notas de cálculo[/]")
        for line in result.electrical.notas:
            console.print(f"  • {line}")


def _export_all(result: ProjectResult, output_dir: Path) -> dict[str, Path]:
    """Genera Excel, PDF, JSON, Markdown, HTML y CSV."""
    return export_bundle(result, output_dir)


def execute_design(inputs: ProjectInputs) -> ProjectResult:
    """Ejecuta el motor de diseño y exporta entregables."""
    _print_banner()
    console.print(
        f"[dim]Potencia={inputs.potencia_kw} kW · Racks={inputs.num_racks} · "
        f"Redundancia={inputs.redundancia.value} · IP{inputs.ip_minimo}[/]\n"
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Calculando y aplicando reglas de diseño…", total=None)
        result = run_design(inputs, version=__version__)

    _print_summary(result, verbose=inputs.verbose)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Generando Excel, PDF, JSON, Markdown, HTML y CSV…", total=None)
        paths = _export_all(result, Path(inputs.output_dir))

    files = Table(title="Entregables generados", box=box.SIMPLE, show_header=True)
    files.add_column("Tipo", style="cyan")
    files.add_column("Ruta")
    labels = {
        "xlsx": "Excel",
        "pdf": "PDF",
        "json": "JSON",
        "md": "Markdown",
        "html": "HTML",
        "csv": "CSV BOM",
    }
    for key, path in paths.items():
        files.add_row(labels.get(key, key), str(path))
    console.print(files)
    console.print("[bold green]✓ Diseño completado correctamente.[/]")
    return result


@app.command("run")
def run_cmd(
    potencia_kw: Optional[float] = typer.Option(
        None, "--potencia-kw", help="Potencia total instalada en kW."
    ),
    num_racks: Optional[int] = typer.Option(
        None, "--num-racks", help="Número de racks / salidas."
    ),
    redundancia: Optional[str] = typer.Option(
        None, "--redundancia", help="Esquema de redundancia: N | N+1 | 2N."
    ),
    ip_minimo: int = typer.Option(
        54, "--ip-minimo", help="Grado de protección IP mínimo (30,31,40,41,54,55,65,66)."
    ),
    carga_armonica: bool = typer.Option(
        False, "--carga-armonica", help="Indica presencia de cargas no lineales (armónicos)."
    ),
    sismico: bool = typer.Option(
        False, "--sismico", help="Requiere resistencia sísmica (IEC 60068-3-3 / UBC Zona 4)."
    ),
    output: str = typer.Option(
        "./output", "--output", help="Carpeta de salida de Excel/PDF/JSON."
    ),
    example: Optional[str] = typer.Option(
        None, "--example", help="Configuración de ejemplo: small | medium | large."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Salida detallada con justificaciones."
    ),
) -> None:
    """
    Configura un tablero TAN-Telecom y genera la documentación técnica.
    """
    try:
        if example:
            name = validate_example_name(example)
            cfg = EXAMPLES[name]
            inputs = build_inputs(
                potencia_kw=cfg["potencia_kw"],
                num_racks=cfg["num_racks"],
                redundancia=cfg["redundancia"],
                ip_minimo=cfg["ip_minimo"],
                carga_armonica=cfg["carga_armonica"],
                sismico=cfg["sismico"],
                output=output,
                verbose=verbose,
                example_name=name,
            )
            console.print(f"[cyan]Usando ejemplo predefinido:[/] [bold]{name}[/]\n")
        else:
            if potencia_kw is None or num_racks is None or redundancia is None:
                raise ValidationError(
                    "Debe indicar --potencia-kw, --num-racks y --redundancia, "
                    "o bien --example small|medium|large."
                )
            inputs = build_inputs(
                potencia_kw=potencia_kw,
                num_racks=num_racks,
                redundancia=redundancia,
                ip_minimo=ip_minimo,
                carga_armonica=carga_armonica,
                sismico=sismico,
                output=output,
                verbose=verbose,
            )
        execute_design(inputs)
    except ValidationError as exc:
        err_console.print(f"[bold red]Error de validación:[/] {exc}")
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # pragma: no cover
        err_console.print(f"[bold red]Error inesperado:[/] {exc}")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1) from exc


# Callback raíz: permite `python main.py --example small` sin subcomando
@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    potencia_kw: Optional[float] = typer.Option(
        None, "--potencia-kw", help="Potencia total instalada en kW."
    ),
    num_racks: Optional[int] = typer.Option(
        None, "--num-racks", help="Número de racks / salidas."
    ),
    redundancia: Optional[str] = typer.Option(
        None, "--redundancia", help="Esquema de redundancia: N | N+1 | 2N."
    ),
    ip_minimo: int = typer.Option(
        54, "--ip-minimo", help="Grado de protección IP mínimo."
    ),
    carga_armonica: bool = typer.Option(
        False, "--carga-armonica", help="Cargas no lineales (armónicos)."
    ),
    sismico: bool = typer.Option(
        False, "--sismico", help="Requisito sísmico."
    ),
    output: str = typer.Option(
        "./output", "--output", help="Carpeta de salida."
    ),
    example: Optional[str] = typer.Option(
        None, "--example", help="Ejemplo: small | medium | large."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Salida detallada."
    ),
    version: bool = typer.Option(
        False, "--version", help="Muestra la versión y sale."
    ),
) -> None:
    """TAN-Telecom — CLI de diseño paramétrico de tableros TAN."""
    if version:
        console.print(f"{__app_name__} v{__version__}")
        raise typer.Exit(code=0)

    if ctx.invoked_subcommand is not None:
        return

    # Sin subcomando: ejecutar flujo principal si hay args útiles
    if example is None and potencia_kw is None and num_racks is None and redundancia is None:
        console.print(ctx.get_help())
        raise typer.Exit(code=0)

    # Reutiliza la misma lógica del comando run
    run_cmd(
        potencia_kw=potencia_kw,
        num_racks=num_racks,
        redundancia=redundancia,
        ip_minimo=ip_minimo,
        carga_armonica=carga_armonica,
        sismico=sismico,
        output=output,
        example=example,
        verbose=verbose,
    )


def run() -> None:
    """Punto de entrada programático."""
    app()


if __name__ == "__main__":
    run()
