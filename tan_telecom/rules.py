"""
Motor de decisión de diseño TAN-Telecom.

Selecciona envolvente XL³, forma de separación interna, familia tipificada
(TT-S / TT-M / TT-E), tabla de verificaciones IEC 61439 y BOM base.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .models import (
    BOMItem,
    ElectricalResults,
    EnclosureRecommendation,
    FormaSeparacion,
    ProjectInputs,
    ProjectResult,
    Redundancia,
    SeparationRecommendation,
    VerificationItem,
    make_project_id,
)
from .calculations import compute_electrical

DATA_DIR = Path(__file__).resolve().parent / "data"
CATALOG_PATH = DATA_DIR / "xl3_catalog.json"


@lru_cache(maxsize=1)
def load_xl3_catalog() -> list[dict[str, Any]]:
    """Carga el catálogo XL³ desde JSON."""
    with CATALOG_PATH.open(encoding="utf-8") as fh:
        payload = json.load(fh)
    return list(payload["envolventes"])


def _ip_cumple(ip_disponibles: list[int], ip_minimo: int) -> bool:
    """True si alguna IP del catálogo es ≥ al mínimo requerido (por dígitos IP)."""
    # Comparación simple por valor entero del código IP (30, 40, 54, 55...)
    return any(ip >= ip_minimo for ip in ip_disponibles)


def _ip_seleccionado(ip_disponibles: list[int], ip_minimo: int) -> int:
    """Elige la IP de catálogo más cercana que cumple el mínimo."""
    candidatos = sorted(ip for ip in ip_disponibles if ip >= ip_minimo)
    if candidatos:
        return candidatos[0]
    return max(ip_disponibles)


def select_enclosure(
    inputs: ProjectInputs,
    electrical: ElectricalResults,
) -> EnclosureRecommendation:
    """
    Selecciona la envolvente XL³ más pequeña que cumple los requisitos.

    Prioridad:
        1. Corriente de selección + margen implícito del catálogo
        2. Icw / Icc
        3. IP mínimo
        4. Requisitos sísmicos
        5. Número de salidas / racks
        6. Menor complejidad / costo relativo
    """
    catalogo = sorted(load_xl3_catalog(), key=lambda e: (e["corriente_max_a"], e["costo_relativo"]))
    in_req = electrical.in_seleccion_a
    icw_req = electrical.icw_requerida_ka
    justificaciones_fallidas: list[str] = []

    elegidas: list[dict[str, Any]] = []
    for env in catalogo:
        motivos_no: list[str] = []
        if env["corriente_max_a"] < in_req:
            motivos_no.append(
                f"In {in_req:.0f} A > Imax {env['corriente_max_a']} A"
            )
        if env["icw_ka"] < icw_req * 0.95:
            motivos_no.append(
                f"Icw catálogo {env['icw_ka']} kA < requerida {icw_req} kA"
            )
        if not _ip_cumple(env["ip_disponibles"], inputs.ip_minimo):
            motivos_no.append(f"IP no alcanza IP{inputs.ip_minimo}")
        if inputs.sismico and not env["resistencia_sismica"]:
            motivos_no.append("sin opción sísmica documentada")
        if inputs.num_racks > env["salidas_max_recomendadas"]:
            motivos_no.append(
                f"salidas {inputs.num_racks} > recomendado {env['salidas_max_recomendadas']}"
            )
        if motivos_no:
            justificaciones_fallidas.append(f"{env['codigo']}: " + "; ".join(motivos_no))
            continue
        elegidas.append(env)

    if not elegidas:
        # Fallback: la de mayor capacidad, documentando incumplimientos residuales
        env = catalogo[-1]
        just = [
            "No se encontró envolvente que cumpla todos los filtros; se selecciona "
            f"la de mayor capacidad ({env['codigo']}) como referencia de escalado.",
            *justificaciones_fallidas[-3:],
        ]
    else:
        env = elegidas[0]
        just = [
            f"Menor envolvente que cumple In de selección {in_req:.0f} A "
            f"(capacidad {env['corriente_max_a']} A).",
            f"Icw/Icc catálogo {env['icw_ka']}/{env['icc_ka']} kA ≥ requeridos "
            f"{electrical.icw_requerida_ka}/{electrical.icc_estimada_ka} kA.",
            f"IP disponible compatible con IP{inputs.ip_minimo} "
            f"(seleccionada IP{_ip_seleccionado(env['ip_disponibles'], inputs.ip_minimo)}).",
            f"Capacidad de salidas: hasta {env['salidas_max_recomendadas']} "
            f"(proyecto: {inputs.num_racks}).",
        ]
        if inputs.sismico:
            just.append("Cumple requisito de resistencia sísmica del catálogo tipificado.")
        if inputs.redundancia == Redundancia.DOS_N:
            just.append("Arquitectura preparada para dual feed en gamas modulares de columnas.")

    alternativas = [e["codigo"] for e in elegidas[1:3]] if elegidas else []

    return EnclosureRecommendation(
        codigo=env["codigo"],
        nombre=env["nombre"],
        corriente_max_a=float(env["corriente_max_a"]),
        icw_ka=float(env["icw_ka"]),
        icc_ka=float(env["icc_ka"]),
        ip_seleccionado=_ip_seleccionado(env["ip_disponibles"], inputs.ip_minimo),
        ip_disponibles=list(env["ip_disponibles"]),
        dimensiones_mm=dict(env["dimensiones_mm"]),
        formas_soportadas=list(env["formas_separacion"]),
        resistencia_sismica=bool(env["resistencia_sismica"]),
        justificacion=just,
        alternativas=alternativas,
    )


def classify_familia(in_sel: float, num_racks: int, redundancia: Redundancia) -> str:
    """
    Clasifica la configuración en familia TAN-Telecom.

    - TT-S: nodos pequeños / acceso
    - TT-M: POP / mediano
    - TT-E: edge denso o alta criticidad compacta
    """
    if in_sel <= 125 and num_racks <= 6 and redundancia == Redundancia.N:
        return "TT-S"
    if in_sel >= 160 and (num_racks >= 8 or redundancia in {Redundancia.N1, Redundancia.DOS_N}):
        return "TT-M"
    if num_racks <= 8 and in_sel <= 250:
        return "TT-E"
    if in_sel <= 160:
        return "TT-S"
    return "TT-M"


def select_separation_form(
    inputs: ProjectInputs,
    electrical: ElectricalResults,
) -> SeparationRecommendation:
    """
    Recomienda forma de separación interna IEC 61439-2.

    Lógica alineada a la memoria TPA / documento Legrand:
    - Preferir 3b o 4b según criticidad.
    - Nodos pequeños N sin armónicos: 2b puede ser suficiente.
    - Mantenimiento en caliente / multi-rack / N+1 / 2N → 3b (preferente) o 4b.
    """
    familia = classify_familia(
        electrical.in_seleccion_a, inputs.num_racks, inputs.redundancia
    )
    criticidad = "media"
    just: list[str] = []
    alternativas: list[str] = []

    alta = (
        inputs.redundancia in {Redundancia.N1, Redundancia.DOS_N}
        or inputs.num_racks >= 8
        or electrical.in_seleccion_a >= 250
        or inputs.sismico
    )
    muy_alta = (
        inputs.redundancia == Redundancia.DOS_N
        and (inputs.num_racks >= 12 or electrical.in_seleccion_a >= 400)
    ) or (inputs.sismico and inputs.carga_armonica and inputs.num_racks >= 10)

    if muy_alta:
        forma = FormaSeparacion.F4B
        criticidad = "muy alta"
        just = [
            "Criticidad muy alta: dual feed y/o alta densidad con requisitos reforzados.",
            "Forma 4b: UF segregadas y bornes en compartimentos individuales, "
            "máxima mantenibilidad y limitación de fallas internas.",
            "Alineado a preferencia de Form 4b en escenarios de SLA extremo (Legrand / IEC 61439-2).",
        ]
        alternativas = ["3b", "4a"]
    elif alta:
        forma = FormaSeparacion.F3B
        criticidad = "alta"
        just = [
            "Criticidad alta (redundancia, multi-rack o corriente media-alta).",
            "Forma 3b: separación barras/UF, separación entre UF y bornes "
            "en zona de cables separada de barras.",
            "Permite intervención selectiva sin exponer todas las unidades funcionales.",
        ]
        if inputs.carga_armonica:
            just.append(
                "Cargas armónicas: se favorece segregación para limitar propagación térmica/eléctrica."
            )
        alternativas = ["4b", "2b"]
    else:
        # Nodo pequeño / edge ligero
        if familia == "TT-E" and inputs.redundancia == Redundancia.N:
            forma = FormaSeparacion.F2B
            criticidad = "media-alta (edge sin dual feed local)"
            just = [
                "Edge site con redundancia N: Forma 2b equilibra costo y protección de barras.",
                "Bornes separados de barras; UF en zona común segregada de barras.",
                "Si el SLA de sitio es alto sin redundancia de building, escalar a 3b.",
            ]
            alternativas = ["3b"]
        else:
            forma = FormaSeparacion.F2B
            criticidad = "media"
            just = [
                "Nodo pequeño / acceso (familia TT-S): Forma 2b es el mejor balance global.",
                "Compartimento de bornes separado de barras; UF en zona común segregada de barras.",
                "Evita sobrecosto de Form 4b sin beneficio operativo medible en este rango.",
            ]
            alternativas = ["3b", "1"]

    if inputs.sismico and forma in {FormaSeparacion.F1, FormaSeparacion.F2A}:
        forma = FormaSeparacion.F3B
        just.append("Requisito sísmico: se eleva la segregación mínima recomendada a 3b.")

    return SeparationRecommendation(
        forma=forma,
        criticidad=criticidad,
        familia_tan=familia,
        justificacion=just,
        alternativas=alternativas,
    )


def build_verifications(
    inputs: ProjectInputs,
    electrical: ElectricalResults,
    enclosure: EnclosureRecommendation,
    separation: SeparationRecommendation,
) -> list[VerificationItem]:
    """
    Construye la tabla de verificaciones de diseño (IEC 61439-1 / Anexo D),
    estructura alineada a la página 8 del documento Legrand.
    """
    cal_ok = "CUMPLE (estimación)" if electrical.calentamiento_ok else "REVISAR (ΔT alta)"
    icc_ok = (
        "CUMPLE (catálogo ≥ req.)"
        if enclosure.icw_ka >= electrical.icw_requerida_ka * 0.95
        else "REVISAR Icw"
    )
    ip_ok = (
        "CUMPLE"
        if enclosure.ip_seleccionado >= inputs.ip_minimo
        else "REVISAR IP"
    )
    sism_obs = (
        "Opción sísmica requerida y cubierta por envolvente tipificada."
        if inputs.sismico and enclosure.resistencia_sismica
        else (
            "Requisito sísmico: verificar kit/ensayo específico del fabricante."
            if inputs.sismico
            else "No requerido en esta configuración."
        )
    )

    filas: list[VerificationItem] = [
        VerificationItem(
            1,
            "Resistencia de materiales y partes (corrosión, estabilidad térmica, "
            "resistencia al fuego, UV, elevación, impacto, marcación)",
            "10.2",
            "SÍ",
            "NO",
            "SÍ*",
            "CUBIERTO por diseño de referencia XL³/TAN",
            "Depende del sistema de envolvente verificado del fabricante original.",
        ),
        VerificationItem(
            2,
            "Grado de protección IP",
            "10.3",
            "SÍ",
            "NO",
            "SÍ",
            ip_ok,
            f"IP requerido IP{inputs.ip_minimo}; seleccionado IP{enclosure.ip_seleccionado}.",
        ),
        VerificationItem(
            3,
            "Distancias de aislación",
            "10.4",
            "SÍ",
            "NO",
            "NO",
            "CUBIERTO (diseño de referencia)",
            "Mantener clearances del sistema de barras y aparatos instalados.",
        ),
        VerificationItem(
            4,
            "Líneas de fuga",
            "10.4",
            "SÍ",
            "NO",
            "NO",
            "CUBIERTO (diseño de referencia)",
            "Verificar contaminación / CTI de materiales en ambiente del sitio.",
        ),
        VerificationItem(
            5,
            "Protección contra descargas eléctricas e integridad de circuitos de protección "
            "(continuidad PE / resistencia ante cortocircuito del PE)",
            "10.5",
            "SÍ",
            "SÍ",
            "NO",
            "A COMPLETAR por ensamblador (ensayo/rutina)",
            "Continuidade PE y bornes de tierra: verificación de rutina obligatoria.",
        ),
        VerificationItem(
            6,
            "Integración de aparatos de conexión y componentes",
            "10.6",
            "NO",
            "NO",
            "SÍ",
            "CUBIERTO por reglas de diseño del sistema",
            f"Forma {separation.forma.value}: respetar kits de segregación y zonas UF.",
        ),
        VerificationItem(
            7,
            "Circuitos internos y conexiones",
            "10.7",
            "NO",
            "NO",
            "SÍ",
            "A COMPLETAR por ensamblador",
            "Cableado interno según secciones y torque de bornes del fabricante.",
        ),
        VerificationItem(
            8,
            "Bornes para conductores externos",
            "10.8",
            "NO",
            "NO",
            "SÍ",
            "CUBIERTO (diseño + forma de separación)",
            f"Forma {separation.forma.value}: bornes en zona conforme a variante a/b.",
        ),
        VerificationItem(
            9,
            "Propiedades dieléctricas (tensión a frecuencia industrial e impulso)",
            "10.9",
            "SÍ",
            "NO",
            "SÍ",
            "CUBIERTO por diseño de referencia / ensayo de tipo",
            "Ue/Ui/Uimp de placa deben declararse en el conjunto final.",
        ),
        VerificationItem(
            10,
            "Límites de calentamiento (elevación de temperatura)",
            "10.10",
            "SÍ",
            "SÍ",
            "SÍ",
            cal_ok,
            (
                f"ΔT estimado {electrical.delta_t_estimado_c} °C "
                f"(límite ref. {electrical.limite_delta_t_c} °C); "
                f"RDF={electrical.rdf}, P_loss≈{electrical.potencia_disipada_w} W. "
                "No sustituye ensayo de tipo."
            ),
        ),
        VerificationItem(
            11,
            "Resistencia a cortocircuitos",
            "10.11",
            "SÍ",
            "SÍ",
            "NO",
            icc_ok,
            (
                f"Icc/Icw requeridos ≈ {electrical.icc_estimada_ka}/"
                f"{electrical.icw_requerida_ka} kA; "
                f"envolvente {enclosure.codigo} Icw/Icc "
                f"{enclosure.icw_ka}/{enclosure.icc_ka} kA."
            ),
        ),
        VerificationItem(
            12,
            "Compatibilidad electromagnética (CEM)",
            "10.12",
            "SÍ",
            "NO",
            "SÍ",
            "CUBIERTO (condiciones de instalación típicas)",
            "En telecomunicaciones, cuidar segregación de potencias y tierras de señal.",
        ),
        VerificationItem(
            13,
            "Funcionamiento mecánico",
            "10.13",
            "SÍ",
            "NO",
            "NO",
            "A COMPLETAR por ensamblador (rutina)",
            "Maniobras de aparatos, enclavamiento y cierre de puertas.",
        ),
        VerificationItem(
            14,
            "Resistencia sísmica / condiciones especiales de servicio",
            "IEC 60068-3-3 / UBC (si aplica)",
            "SÍ",
            "SÍ",
            "SÍ",
            "APLICA" if inputs.sismico else "N/A",
            sism_obs,
        ),
    ]
    return filas


def build_bom(
    inputs: ProjectInputs,
    electrical: ElectricalResults,
    enclosure: EnclosureRecommendation,
    separation: SeparationRecommendation,
) -> list[BOMItem]:
    """Genera una lista de materiales tipificada (no cotización comercial)."""
    forma = separation.forma.value
    n = inputs.num_racks
    bom: list[BOMItem] = [
        BOMItem(
            codigo=f"ENV-{enclosure.codigo}",
            descripcion=f"Envolvente {enclosure.nombre} IP{enclosure.ip_seleccionado}",
            cantidad=1,
            unidad="u",
            categoria="Envolvente",
            observaciones=f"In max {enclosure.corriente_max_a} A",
        ),
        BOMItem(
            codigo="BAR-CU-MAIN",
            descripcion=f"Juego de barras de cobre dimensionado a {electrical.in_seleccion_a:.0f} A",
            cantidad=1,
            unidad="juego",
            categoria="Barras",
            observaciones=f"Icw ref. {electrical.icw_requerida_ka} kA",
        ),
        BOMItem(
            codigo="QG-MAIN",
            descripcion=f"Interruptor/seccionador general {electrical.in_seleccion_a:.0f} A",
            cantidad=2 if inputs.redundancia == Redundancia.DOS_N else 1,
            unidad="u",
            categoria="Aparatos",
            observaciones=f"Redundancia {inputs.redundancia.value}",
        ),
        BOMItem(
            codigo=f"KIT-FORM-{forma.upper()}",
            descripcion=f"Kit de segregación interna Forma {forma}",
            cantidad=1,
            unidad="juego",
            categoria="Separación",
            observaciones="Plastrones, tabiques, canalizaciones de forma",
        ),
        BOMItem(
            codigo="UF-RACK-OUT",
            descripcion="Unidades funcionales / salidas a racks",
            cantidad=n,
            unidad="u",
            categoria="Salidas",
            observaciones="Protecciones por rack tipificadas",
        ),
        BOMItem(
            codigo="UF-CLIMA",
            descripcion="Salida clima / ventilación",
            cantidad=1,
            unidad="u",
            categoria="Salidas",
        ),
        BOMItem(
            codigo="UF-UPS",
            descripcion="Salida UPS / servicios críticos",
            cantidad=1 if inputs.redundancia != Redundancia.N else 1,
            unidad="u",
            categoria="Salidas",
        ),
        BOMItem(
            codigo="UF-AUX",
            descripcion="Auxiliares (iluminación tablero, tomas de servicio)",
            cantidad=1,
            unidad="u",
            categoria="Salidas",
        ),
        BOMItem(
            codigo="BOR-EXT",
            descripcion="Bornes para conductores externos + PE",
            cantidad=1,
            unidad="juego",
            categoria="Conexionado",
            observaciones="Zona de cables según forma a/b",
        ),
        BOMItem(
            codigo="ID-PLATE",
            descripcion="Placa de características IEC 61439 + marcaje TAN-Telecom",
            cantidad=1,
            unidad="u",
            categoria="Documentación",
        ),
        BOMItem(
            codigo="DOC-PACK",
            descripcion="Paquete documental (unifilar, verificaciones, declaración)",
            cantidad=1,
            unidad="u",
            categoria="Documentación",
        ),
    ]
    if inputs.redundancia in {Redundancia.N1, Redundancia.DOS_N}:
        bom.append(
            BOMItem(
                codigo="COUPLER-OPT",
                descripcion="Preparación acoplamiento / segunda acometida",
                cantidad=1,
                unidad="u",
                categoria="Aparatos",
                observaciones="Dual feed / reserva de columna",
            )
        )
    if inputs.carga_armonica:
        bom.append(
            BOMItem(
                codigo="NEUTRO-SOBRE",
                descripcion="Neutro sobredimensionado / atención a armónicos 3er orden",
                cantidad=1,
                unidad="u",
                categoria="Barras",
                observaciones="Buena práctica con cargas no lineales IT",
            )
        )
    return bom


def run_design(inputs: ProjectInputs, version: str = "1.0.0") -> ProjectResult:
    """
    Orquesta el diseño completo: cálculo → reglas → verificaciones → BOM.

    Args:
        inputs: Parámetros validados.
        version: Versión de la herramienta.

    Returns:
        ProjectResult listo para generar entregables.
    """
    electrical = compute_electrical(inputs)
    enclosure = select_enclosure(inputs, electrical)
    separation = select_separation_form(inputs, electrical)
    verifications = build_verifications(inputs, electrical, enclosure, separation)
    bom = build_bom(inputs, electrical, enclosure, separation)

    warnings: list[str] = []
    if not electrical.calentamiento_ok:
        warnings.append(
            f"Calentamiento estimado {electrical.delta_t_estimado_c} °C supera "
            f"{electrical.limite_delta_t_c} °C de referencia."
        )
    if enclosure.icw_ka < electrical.icw_requerida_ka:
        warnings.append(
            "La Icw de la envolvente seleccionada es inferior a la estimada requerida."
        )
    if inputs.sismico and not enclosure.resistencia_sismica:
        warnings.append("Requisito sísmico no cubierto plenamente por el catálogo tipificado.")

    from datetime import datetime, timezone

    return ProjectResult(
        project_id=make_project_id(separation.familia_tan),
        version=version,
        generated_at=datetime.now(timezone.utc).isoformat(),
        inputs=inputs,
        electrical=electrical,
        enclosure=enclosure,
        separation=separation,
        verifications=verifications,
        bom=bom,
        warnings=warnings,
    )
