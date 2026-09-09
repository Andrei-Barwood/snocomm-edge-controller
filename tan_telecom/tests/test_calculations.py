"""Tests unitarios básicos de cálculos eléctricos."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tan_telecom.calculations import (
    corriente_nominal_base,
    normalizar_corriente,
    rdf_por_circuitos,
    compute_electrical,
)
from tan_telecom.models import ProjectInputs, Redundancia
from tan_telecom.validators import build_inputs, ValidationError


def test_corriente_nominal_base_45kw():
    in_a = corriente_nominal_base(45.0, 400.0, 0.9, 0.95)
    expected = (45 * 1000) / (math.sqrt(3) * 400 * 0.9 * 0.95)
    assert abs(in_a - expected) < 0.01
    assert 70 < in_a < 85  # ~76 A


def test_normalizar_corriente():
    assert normalizar_corriente(76.2) == 80
    assert normalizar_corriente(125) == 125
    assert normalizar_corriente(126) == 160


def test_rdf():
    assert rdf_por_circuitos(1) == 1.0
    assert rdf_por_circuitos(4) == 0.8
    assert rdf_por_circuitos(20) == 0.5


def test_compute_electrical_small():
    inputs = ProjectInputs(
        potencia_kw=45,
        num_racks=4,
        redundancia=Redundancia.N,
        ip_minimo=54,
    )
    res = compute_electrical(inputs)
    assert res.in_base_a > 0
    assert res.in_seleccion_a >= res.in_diseno_a
    assert 0.5 <= res.rdf <= 1.0
    assert res.limite_delta_t_c == 30.0


def test_build_inputs_invalid_ip():
    with pytest.raises(ValidationError):
        build_inputs(potencia_kw=10, num_racks=2, redundancia="N", ip_minimo=99)


def test_build_inputs_ok(tmp_path):
    inp = build_inputs(
        potencia_kw=45,
        num_racks=4,
        redundancia="N+1",
        output=str(tmp_path),
    )
    assert inp.redundancia == Redundancia.N1
