"""
Modelos de datos del proyecto TAN-Telecom.

Define estructuras tipadas para entradas, resultados de cálculo,
recomendaciones de diseño y el paquete de configuración completo.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Redundancia(str, Enum):
    """Esquema de redundancia eléctrica del nodo."""

    N = "N"
    N1 = "N+1"
    DOS_N = "2N"


class FormaSeparacion(str, Enum):
    """Formas de separación interna según IEC 61439-2."""

    F1 = "1"
    F2A = "2a"
    F2B = "2b"
    F3A = "3a"
    F3B = "3b"
    F4A = "4a"
    F4B = "4b"


@dataclass
class ProjectInputs:
    """Parámetros de entrada del proyecto."""

    potencia_kw: float
    num_racks: int
    redundancia: Redundancia
    ip_minimo: int = 54
    carga_armonica: bool = False
    sismico: bool = False
    output_dir: str = "./output"
    verbose: bool = False
    example_name: str | None = None
    tension_v: float = 400.0
    cos_phi: float = 0.9
    rendimiento: float = 0.95

    def to_dict(self) -> dict[str, Any]:
        """Serializa entradas a diccionario JSON-compatible."""
        data = asdict(self)
        data["redundancia"] = self.redundancia.value
        return data


@dataclass
class ElectricalResults:
    """Resultados de cálculos eléctricos de predimensionamiento."""

    in_base_a: float
    factor_redundancia: float
    in_diseno_a: float
    in_seleccion_a: float
    icc_estimada_ka: float
    icw_requerida_ka: float
    rdf: float
    factor_simultaneidad: float
    factor_utilizacion: float
    potencia_disipada_w: float
    delta_t_estimado_c: float
    calentamiento_ok: bool
    limite_delta_t_c: float = 30.0
    formula_in: str = ""
    notas: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serializa resultados eléctricos."""
        return asdict(self)


@dataclass
class EnclosureRecommendation:
    """Envolvente XL³ seleccionada y justificación."""

    codigo: str
    nombre: str
    corriente_max_a: float
    icw_ka: float
    icc_ka: float
    ip_seleccionado: int
    ip_disponibles: list[int]
    dimensiones_mm: dict[str, Any]
    formas_soportadas: list[str]
    resistencia_sismica: bool
    justificacion: list[str]
    alternativas: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serializa recomendación de envolvente."""
        return asdict(self)


@dataclass
class SeparationRecommendation:
    """Forma de separación interna recomendada."""

    forma: FormaSeparacion
    criticidad: str
    familia_tan: str
    justificacion: list[str]
    alternativas: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serializa recomendación de forma."""
        data = asdict(self)
        data["forma"] = self.forma.value
        return data


@dataclass
class VerificationItem:
    """Ítem de la tabla de verificaciones de diseño IEC 61439-1."""

    numero: int
    caracteristica: str
    articulo: str
    ensayos: str
    comparacion: str
    evaluacion: str
    estado: str
    observaciones: str

    def to_dict(self) -> dict[str, Any]:
        """Serializa ítem de verificación."""
        return asdict(self)


@dataclass
class BOMItem:
    """Línea de lista de materiales tipificada."""

    codigo: str
    descripcion: str
    cantidad: float
    unidad: str
    categoria: str
    observaciones: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serializa ítem BOM."""
        return asdict(self)


@dataclass
class ProjectResult:
    """Configuración completa generada por TAN-Telecom."""

    project_id: str
    version: str
    generated_at: str
    inputs: ProjectInputs
    electrical: ElectricalResults
    enclosure: EnclosureRecommendation
    separation: SeparationRecommendation
    verifications: list[VerificationItem]
    bom: list[BOMItem]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serializa el resultado completo a JSON."""
        return {
            "project_id": self.project_id,
            "version": self.version,
            "generated_at": self.generated_at,
            "inputs": self.inputs.to_dict(),
            "electrical": self.electrical.to_dict(),
            "enclosure": self.enclosure.to_dict(),
            "separation": self.separation.to_dict(),
            "verifications": [v.to_dict() for v in self.verifications],
            "bom": [b.to_dict() for b in self.bom],
            "warnings": self.warnings,
        }


def make_project_id(prefix: str = "TT") -> str:
    """Genera un identificador de proyecto con marca temporal UTC."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{stamp}"
