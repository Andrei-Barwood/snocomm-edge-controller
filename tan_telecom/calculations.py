"""
Cálculos eléctricos de predimensionamiento para tableros TAN-Telecom.

Implementa corrientes nominales, estimación de cortocircuito, RDF y
verificación simplificada de calentamiento (ΔT < 30 °C, criterio de
referencia documental Legrand / práctica de tableros BT).

Notas de ingeniería:
- Los valores de Icc/Icw son estimaciones conservadoras de tipología
  telecomunicaciones, no un estudio de cortocircuito de red.
- El modelo térmico es de predimensionamiento académico y no reemplaza
  ensayo de elevación de temperatura IEC 61439-1 §10.10.
"""

from __future__ import annotations

import math
from typing import Final

from .models import ElectricalResults, ProjectInputs, Redundancia

# Constantes de diseño por defecto
V_DEFAULT: Final[float] = 400.0
COS_PHI_DEFAULT: Final[float] = 0.9
ETA_DEFAULT: Final[float] = 0.95
DELTA_T_LIMITE_C: Final[float] = 30.0

# Factores de capacidad de diseño según esquema de redundancia.
# N: dimensionamiento a la carga calculada.
# N+1: margen para continuidad con elemento de reserva (típicamente 15–25 %).
# 2N: cada camino alimenta la carga completa; el tablero se dimensiona a In
#     de la carga, pero se eleva el margen de cortocircuito y se documenta dual feed.
FACTOR_REDUNDANCIA: Final[dict[Redundancia, float]] = {
    Redundancia.N: 1.00,
    Redundancia.N1: 1.20,
    Redundancia.DOS_N: 1.05,
}

# Corrientes normalizadas de selección de tablero (A)
CORRIENTES_NORMALIZADAS: Final[tuple[int, ...]] = (
    16, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800,
    1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6300,
)


def corriente_nominal_base(
    potencia_kw: float,
    tension_v: float = V_DEFAULT,
    cos_phi: float = COS_PHI_DEFAULT,
    eta: float = ETA_DEFAULT,
) -> float:
    """
    Calcula la corriente nominal trifásica base.

    Fórmula:
        In = (P · 1000) / (√3 · V · cosφ · η)

    Args:
        potencia_kw: Potencia total instalada en kW.
        tension_v: Tensión de línea en V.
        cos_phi: Factor de potencia.
        eta: Rendimiento / factor de eficiencia del conjunto.

    Returns:
        Corriente nominal base en amperios.
    """
    if potencia_kw <= 0:
        raise ValueError("La potencia debe ser positiva.")
    if tension_v <= 0 or cos_phi <= 0 or eta <= 0:
        raise ValueError("Tensión, cosφ y η deben ser positivos.")
    return (potencia_kw * 1000.0) / (math.sqrt(3.0) * tension_v * cos_phi * eta)


def factor_redundancia(redundancia: Redundancia) -> float:
    """Devuelve el factor de diseño asociado al esquema de redundancia."""
    return FACTOR_REDUNDANCIA[redundancia]


def normalizar_corriente(in_a: float) -> float:
    """
    Redondea la corriente de diseño a la corriente normalizada superior.

    Args:
        in_a: Corriente de diseño calculada [A].

    Returns:
        Corriente de selección normalizada [A].
    """
    for valor in CORRIENTES_NORMALIZADAS:
        if valor >= in_a - 1e-9:
            return float(valor)
    return float(CORRIENTES_NORMALIZADAS[-1])


def rdf_por_circuitos(num_circuitos: int) -> float:
    """
    Factor de diversidad asignado (RDF) según número de circuitos/salidas.

    Basado en rangos habituales de IEC 61439 / práctica de distribución
    (valores tipificados para predimensionamiento).

    Args:
        num_circuitos: Número de salidas / racks.

    Returns:
        RDF entre 0.5 y 1.0.
    """
    n = max(1, num_circuitos)
    if n == 1:
        return 1.0
    if n <= 3:
        return 0.9
    if n <= 5:
        return 0.8
    if n <= 9:
        return 0.7
    if n <= 15:
        return 0.6
    return 0.5


def factor_simultaneidad(num_racks: int) -> float:
    """
    Factor de simultaneidad de cargas de racks de telecomunicaciones.

    En nodos IT no todas las salidas operan a plena carga a la vez.
    """
    if num_racks <= 2:
        return 0.95
    if num_racks <= 6:
        return 0.85
    if num_racks <= 12:
        return 0.75
    return 0.70


def factor_utilizacion(carga_armonica: bool, redundancia: Redundancia) -> float:
    """
    Factor de utilización efectivo del conjunto.

    Las cargas no lineales (armónicos) y la redundancia 2N elevan la
    solicitación térmica efectiva sobre barras y aparatos.
    """
    base = 0.80
    if carga_armonica:
        base += 0.08  # mayor pérdida en conductores / N por armónicos
    if redundancia == Redundancia.DOS_N:
        base += 0.05
    return min(base, 0.98)


def estimar_icc_ka(
    in_seleccion_a: float,
    potencia_kw: float,
    redundancia: Redundancia,
) -> tuple[float, float]:
    """
    Estima Icc e Icw requeridas de forma conservadora.

    Heurística de telecomunicaciones:
    - Nodos pequeños (< 100 A): red de baja Icc típica 10–25 kA
    - Medianos: 25–36 kA
    - Grandes / 2N: 36–50+ kA

    Returns:
        Tupla (Icc_kA, Icw_kA).
    """
    if in_seleccion_a <= 125:
        icc = 16.0
    elif in_seleccion_a <= 250:
        icc = 25.0
    elif in_seleccion_a <= 630:
        icc = 36.0
    elif in_seleccion_a <= 1600:
        icc = 50.0
    else:
        icc = 65.0

    # Ajuste por potencia bruta y dual feed (posible contribución de dos fuentes)
    if potencia_kw >= 200:
        icc = max(icc, 36.0)
    if potencia_kw >= 300:
        icc = max(icc, 50.0)
    if redundancia == Redundancia.DOS_N:
        icc = min(icc * 1.15, 100.0)

    icw = icc  # para predimensionamiento se iguala Icw ≈ Icc condicional
    return round(icc, 1), round(icw, 1)


def estimar_potencia_disipada_w(
    in_diseno_a: float,
    rdf: float,
    factor_utilizacion: float,
    carga_armonica: bool,
) -> float:
    """
    Estima pérdidas disipadas en el conjunto (W).

    Modelo simplificado de predimensionamiento:
        P_loss ≈ k · In_diseño · RDF · Ku · (1 + k_h)

    k ≈ 0.55 W/A refleja pérdidas típicas de aparatos + barras en tableros BT
    de telecomunicaciones (orden de magnitud; no sustituye ensayo 10.10).
    """
    k = 0.55
    k_h = 0.12 if carga_armonica else 0.0
    return max(0.0, k * in_diseno_a * rdf * factor_utilizacion * (1.0 + k_h))


def estimar_delta_t_c(
    potencia_disipada_w: float,
    in_seleccion_a: float,
    num_racks: int,
    ip_minimo: int,
) -> float:
    """
    Estima elevación de temperatura interna del tablero [°C].

    Modelo térmico de predimensionamiento calibrado para nodos telecom:
    - ΔT base por carga relativa y disipación.
    - Penalización moderada por IP alto (menor ventilación natural).
    - Penalización por densidad de salidas.

    Criterio de aceptación de referencia: ΔT < 30 °C
    (Anexo / práctica de elevación de temperatura en documentación Legrand).
    """
    # Capacidad térmica / disipación asociada al tamaño de envolvente (proxy In)
    if in_seleccion_a <= 160:
        k_disip = 2.8  # W/K aparente
    elif in_seleccion_a <= 400:
        k_disip = 4.5
    elif in_seleccion_a <= 800:
        k_disip = 7.0
    elif in_seleccion_a <= 4000:
        k_disip = 14.0
    else:
        k_disip = 20.0

    if ip_minimo >= 65:
        r_ip = 1.25
    elif ip_minimo >= 54:
        r_ip = 1.12
    elif ip_minimo >= 40:
        r_ip = 1.05
    else:
        r_ip = 1.00

    # Densidad de salidas: más UF → más pérdidas locales y menos convección libre
    r_dens = 1.0 + min(0.25, max(0.0, (num_racks - 4) * 0.02))

    delta_t = (potencia_disipada_w / k_disip) * r_ip * r_dens
    # Rango realista de operación en tableros BT cargados
    return round(min(55.0, max(10.0, delta_t)), 1)


def compute_electrical(inputs: ProjectInputs) -> ElectricalResults:
    """
    Ejecuta la cadena completa de cálculos eléctricos.

    Args:
        inputs: Parámetros validados del proyecto.

    Returns:
        ElectricalResults con corrientes, Icc/Icw, RDF y calentamiento.
    """
    in_base = corriente_nominal_base(
        potencia_kw=inputs.potencia_kw,
        tension_v=inputs.tension_v,
        cos_phi=inputs.cos_phi,
        eta=inputs.rendimiento,
    )
    f_red = factor_redundancia(inputs.redundancia)
    in_diseno = in_base * f_red
    in_sel = normalizar_corriente(in_diseno)
    rdf = rdf_por_circuitos(inputs.num_racks)
    f_sim = factor_simultaneidad(inputs.num_racks)
    f_util = factor_utilizacion(inputs.carga_armonica, inputs.redundancia)
    icc, icw = estimar_icc_ka(in_sel, inputs.potencia_kw, inputs.redundancia)
    p_loss = estimar_potencia_disipada_w(
        in_diseno_a=in_diseno,
        rdf=rdf,
        factor_utilizacion=f_util,
        carga_armonica=inputs.carga_armonica,
    )
    delta_t = estimar_delta_t_c(
        potencia_disipada_w=p_loss,
        in_seleccion_a=in_sel,
        num_racks=inputs.num_racks,
        ip_minimo=inputs.ip_minimo,
    )
    ok = delta_t < DELTA_T_LIMITE_C

    notas: list[str] = [
        f"In base calculada a {inputs.tension_v:.0f} V, cosφ={inputs.cos_phi}, η={inputs.rendimiento}.",
        f"Factor de redundancia ({inputs.redundancia.value}) = {f_red:.2f}.",
        f"RDF = {rdf:.2f} para {inputs.num_racks} circuitos/salidas.",
    ]
    if inputs.carga_armonica:
        notas.append(
            "Cargas armónicas activas: se incrementó utilización y pérdidas (efecto N y disipación)."
        )
    if not ok:
        notas.append(
            f"ΔT estimado {delta_t:.1f} °C ≥ {DELTA_T_LIMITE_C:.0f} °C: se recomienda "
            "mayor envolvente, menor compactación o ventilación forzada."
        )
    if inputs.redundancia == Redundancia.DOS_N:
        notas.append(
            "Arquitectura 2N: dimensionar cada acometida/general para la carga completa; "
            "preparar dual feed / acoplamiento."
        )

    formula = (
        f"In = (P·1000)/(√3·V·cosφ·η) = "
        f"({inputs.potencia_kw}·1000)/(√3·{inputs.tension_v}·{inputs.cos_phi}·{inputs.rendimiento})"
    )

    return ElectricalResults(
        in_base_a=round(in_base, 2),
        factor_redundancia=f_red,
        in_diseno_a=round(in_diseno, 2),
        in_seleccion_a=in_sel,
        icc_estimada_ka=icc,
        icw_requerida_ka=icw,
        rdf=rdf,
        factor_simultaneidad=f_sim,
        factor_utilizacion=round(f_util, 3),
        potencia_disipada_w=round(p_loss, 1),
        delta_t_estimado_c=delta_t,
        calentamiento_ok=ok,
        limite_delta_t_c=DELTA_T_LIMITE_C,
        formula_in=formula,
        notas=notas,
    )
