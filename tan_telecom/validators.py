"""
Validaciones de entrada y de coherencia de diseño.

Separa las reglas de validación de la lógica de cálculo y de la CLI
para facilitar pruebas unitarias y mensajes de error consistentes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .models import ProjectInputs, Redundancia

IP_PERMITIDOS: frozenset[int] = frozenset({30, 31, 40, 41, 54, 55, 65, 66})
REDUNDANCIAS_VALIDAS: frozenset[str] = frozenset({"N", "N+1", "2N"})
EXAMPLES_VALIDOS: frozenset[str] = frozenset({"small", "medium", "large"})


class ValidationError(ValueError):
    """Error de validación de parámetros de usuario o de diseño."""


def validate_ip_minimo(ip_minimo: int) -> int:
    """Valida que el grado IP esté en el conjunto admitido."""
    if ip_minimo not in IP_PERMITIDOS:
        permitidos = ", ".join(str(x) for x in sorted(IP_PERMITIDOS))
        raise ValidationError(
            f"IP mínimo inválido: {ip_minimo}. Valores admitidos: {permitidos}."
        )
    return ip_minimo


def validate_potencia(potencia_kw: float) -> float:
    """Valida potencia instalada positiva."""
    if potencia_kw is None or potencia_kw <= 0:
        raise ValidationError("La potencia (--potencia-kw) debe ser mayor que 0.")
    if potencia_kw > 5000:
        raise ValidationError(
            "Potencia fuera de rango de predimensionamiento (máx. 5000 kW)."
        )
    return float(potencia_kw)


def validate_num_racks(num_racks: int) -> int:
    """Valida número de racks / salidas."""
    if num_racks is None or num_racks < 1:
        raise ValidationError("El número de racks (--num-racks) debe ser ≥ 1.")
    if num_racks > 200:
        raise ValidationError("Número de racks excesivo para el alcance de la herramienta.")
    return int(num_racks)


def parse_redundancia(value: str) -> Redundancia:
    """Convierte la cadena de redundancia a enumeración."""
    key = (value or "").strip().upper().replace(" ", "")
    mapping = {
        "N": Redundancia.N,
        "N+1": Redundancia.N1,
        "N1": Redundancia.N1,
        "2N": Redundancia.DOS_N,
    }
    if key not in mapping:
        raise ValidationError(
            f"Redundancia inválida: '{value}'. Use N, N+1 o 2N."
        )
    return mapping[key]


def validate_example_name(name: str) -> str:
    """Valida el identificador de ejemplo predefinido."""
    key = (name or "").strip().lower()
    if key not in EXAMPLES_VALIDOS:
        raise ValidationError(
            f"Ejemplo desconocido: '{name}'. Use small, medium o large."
        )
    return key


def validate_output_dir(path: str | Path) -> Path:
    """Normaliza y prepara la carpeta de salida."""
    out = Path(path).expanduser().resolve()
    try:
        out.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ValidationError(f"No se pudo crear la carpeta de salida: {out}") from exc
    return out


def build_inputs(
    *,
    potencia_kw: float,
    num_racks: int,
    redundancia: str,
    ip_minimo: int = 54,
    carga_armonica: bool = False,
    sismico: bool = False,
    output: str = "./output",
    verbose: bool = False,
    example_name: str | None = None,
) -> ProjectInputs:
    """Construye y valida un objeto ProjectInputs."""
    return ProjectInputs(
        potencia_kw=validate_potencia(potencia_kw),
        num_racks=validate_num_racks(num_racks),
        redundancia=parse_redundancia(redundancia),
        ip_minimo=validate_ip_minimo(ip_minimo),
        carga_armonica=bool(carga_armonica),
        sismico=bool(sismico),
        output_dir=str(validate_output_dir(output)),
        verbose=bool(verbose),
        example_name=example_name,
    )


def format_errors(errors: Iterable[str]) -> str:
    """Formatea una lista de errores para presentación en CLI."""
    lines = [f"  • {e}" for e in errors]
    return "Errores de validación:\n" + "\n".join(lines)
