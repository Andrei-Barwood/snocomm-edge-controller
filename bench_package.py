"""Paquete documental del banco físico 24 V para el TPA (aún sin potencia)."""

from __future__ import annotations

from typing import Any


def bench_package() -> dict[str, Any]:
    return {
        "title": "Banco físico 24 VDC / ≤ 120 W — pañol CFT Paillaco",
        "status": "diseño académico — este software no energiza el banco",
        "voltage_class": "24 VDC limitada, techo de fuente 30 V",
        "forbidden": "48 V, 400 V, 500 kW, ~700 A, 380/400 VAC, o red de cliente",
        "inventory": "docs/INVENTARIO_PANOL_CFT_PAILLACO.md",
        "panol": "Pañol CFT Paillaco",
        "physical_outputs_available": False,
        "layers": {
            "A": "Software SIL: 24 V / 120 W simulados (5 A, techo 30 V, OV 29 V). physical_outputs_available = false. Sin GPIO.",
            "B": "Banco físico TPA: 24 VDC, wanptek KPS305D + Gratten GA1102CAL. Este software no energiza la fuente.",
            "C": "Fuera de TPA: 48 V, MCU/PWM/puente, 400 V.",
        },
        "sil": {
            "voltage_v": 24.0,
            "current_a": 5.0,
            "power_w": 120.0,
            "source_ceiling_v": 30.0,
            "overvoltage_trip_v": 29.0,
            "physical_outputs_available": False,
        },
        "source": {
            "instrument": "wanptek KPS305D",
            "plate": "0–30 V / 0–5 A",
            "work_point_v": 24.0,
            "current_limit_a": 5.0,
            "demo_ilimit_a": 0.50,
        },
        "scope": {
            "instrument": "Gratten GA1102CAL",
            "bandwidth_mhz": 100,
            "channels": 2,
            "sample_gsa": 1.0,
        },
        "unifilar": [
            "wanptek KPS305D a 24,0 V, Ilim 0,50 A, modo C.V.",
            "Interruptor I/O de la fuente como corte de energía del ensayo",
            "Carga resistiva de pañol P < 120 W, I < Ilim",
            "Gratten GA1102CAL CH1 en bornes ± (ref. en −; Probe 1x/10x si hay sonda el día del lab)",
            "CSV USB Time,CH1 → Monitor AHF (mapear CH1 a va)",
            "Sin puente MOSFET, sin 48 V, sin 400 V, sin red AC",
        ],
        "risks": [
            {
                "id": "R1",
                "hazard": "Energizar la KPS305D sin Ilim ni clase A",
                "mitigation": "Ilim 0,50 A ANTES de subir V; switch en O hasta checklist; clase A presente",
            },
            {
                "id": "R2",
                "hazard": "Rearme automático tras sobrecorriente o E-stop (modelo SIL)",
                "mitigation": "Falla enclavada en power_stage/; reset manual. La fuente no la rearma el PC.",
            },
            {
                "id": "R3",
                "hazard": "Creer que el laptop corta la fuente",
                "mitigation": "physical_outputs_available = false. Corte físico = switch I/O de la KPS305D.",
            },
            {
                "id": "R4",
                "hazard": "Contacto con 24 V vivos o bornes invertidos",
                "mitigation": "Descarga comprobada (0 V en display y Gratten), pantalla, clase A",
            },
        ],
        "cft_bom": [
            {
                "item": "wanptek KPS305D 0–30 V / 0–5 A (punto 24,0 V, Ilim)",
                "source": "Pañol CFT Paillaco",
                "status": "USABLE EN TPA",
            },
            {
                "item": "Gratten GA1102CAL 100 MHz 2 ch 1 GSa/s, USB CSV/BMP",
                "source": "Pañol CFT Paillaco",
                "status": "USABLE EN TPA",
            },
            {
                "item": "Punta CH1 1x/10x pasiva (pendiente de verificar el día del lab; no fotografiada)",
                "source": "NO FOTOGRAFIADO",
                "status": "NO FOTOGRAFIADO",
            },
            {
                "item": "Carga resistiva de pañol P < 120 W, I < Ilim (valor el día del lab; no fotografiada)",
                "source": "NO FOTOGRAFIADO",
                "status": "NO FOTOGRAFIADO",
            },
            {
                "item": "Pendrive FAT32 para CSV del Gratten",
                "source": "Pañol CFT Paillaco",
                "status": "SOLO APOYO",
            },
            {
                "item": "Segunda persona licencia clase A si hay 24 V energizados",
                "source": "Procedimiento A5",
                "status": "USABLE EN TPA",
            },
        ],
        "procedure": [
            "SIL en el laptop: POWER_OFF → READY → RUN, E-stop y latch, sin GPIO.",
            "KPS305D en O. Ilim 0,50 A, luego V = 24,0 V.",
            "Clase A presente. Carga < 120 W. Punta CH1 en bornes ±.",
            "Energizar (I). LED C.V. Contrastar display ≈ Mean del Gratten.",
            "SAVE CSV USB; import Monitor AHF mapeando CH1 → va.",
            "Switch O. Comprobar 0 V en fuente y en el Gratten.",
            "Un DC de 24 V no demuestra H3/H5/H7; el DSP se defiende con patrón sintético.",
        ],
        "acceptance": [
            {"id": "A1", "criterion": "Ninguna salida física desde este software (physical_outputs_available = false)."},
            {"id": "A2", "criterion": "E-stop y sobrecorriente enclavados; no hay rearranque automático."},
            {"id": "A3", "criterion": "Precarga del modelo HIL alcanza ≥ 90 % de Vdc; no hay DC-link físico ni puente."},
            {"id": "A4", "criterion": "El DSP se valida primero con señales patrón; no se usa el THDi del dashboard como evidencia SEC."},
            {"id": "A5", "criterion": "Toda prueba energizada con pantalla, descarga comprobada y segunda persona competente."},
        ],
    }
