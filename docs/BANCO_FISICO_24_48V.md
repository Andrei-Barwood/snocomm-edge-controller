# Retirado — el banco del TPA es 24 V, no 24–48 V

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco  
**Enmienda:** 21-ago-2026

Este archivo quedó como puntero. El nombre `24_48V` es histórico.
**48 V reales no caben** en la wanptek KPS305D (0–30 V / 0–5 A, techo 30 V).
No se pide una “fuente 24–48 V” ni sondas diferenciales.

| Documento | Rol |
|---|---|
| `docs/BANCO_FISICO_24V.md` | Paquete vigente (unifilar, riesgos, A1–A5) |
| `docs/INVENTARIO_PANOL_CFT_PAILLACO.md` | Material fotografiado 21-ago-2026 |
| `docs/POWER_STAGE_24V.md` | HIL vigente 24 V / 120 W |
| `docs/POWER_STAGE_48V.md` | Simulación 48 V / 500 W **retirada** del alcance |

## BOM del pañol (no es catálogo de 48 V)

Fuente: **Pañol CFT Paillaco**.

| Ítem | Estado |
|---|---|
| wanptek KPS305D, 0–30 V / 0–5 A, punto 24,0 V, Ilim | USABLE EN TPA |
| Gratten GA1102CAL, 100 MHz, 2 ch, 1 GSa/s, USB CSV/BMP | USABLE EN TPA |
| Segunda fuente, sondas, carga, E-stop, generador | NO FOTOGRAFIADO — no inventar |
| 48 V reales, 380/400 VAC, 500 kW, ~700 A | NO USAR EN TPA |

La API `GET /api/bench/package` expone este BOM. El software no energiza
la fuente.
