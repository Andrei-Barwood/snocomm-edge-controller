# Carta Gantt del TPA

**Proyecto:** Controlador de borde para filtro activo de armónicos (AHF)
**Repositorio:** `snocomm-edge-controller`
**Periodo:** 08-jun-2026 — 06-dic-2026 (26 semanas)
**Fecha de estado:** 23-ago-2026
**Avance ponderado:** 84 %

Documento de programación del Trabajo Práctico Aplicado. El PDF de entrega es `CARTA_GANTT_TPA.pdf` (A3 apaisado, 3 láminas). El CSV `CARTA_GANTT_TPA.csv` importa a Excel o LibreOffice Calc (separador `;`).

## Alcance que programa esta carta

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

Preingeniería de tableros BT (IEC 61439 / TAN), DSP 3P+N sobre señales patrón y validación SIL del banco 24 V (KPS305D). **Hoy calcula y simula; no mide con instrumento certificado ni inyecta corriente.**

## Gantt (Mermaid)

```mermaid
gantt
    title TPA AHF Edge Controller — jun a dic 2026
    dateFormat  YYYY-MM-DD
    axisFormat  %d %b
    todayMarker on
    excludes    weekends

    section F0 Gestion
    Kickoff y alcance                 :done, 0_1, 2026-06-08, 14d
    Revision normativa IEC/RIC        :done, 0_2, 2026-06-08, 28d
    EDT, riesgos y carta Gantt        :done, 0_3, 2026-06-15, 14d

    section F1 Arquitectura
    Procesos IPC y supervisory        :done, 1_1, 2026-06-15, 21d
    Docker, ADC y shared memory       :done, 1_2, after 1_1, 21d

    section F2 TAN IEC 61439
    Calculos I / Icw / calentamiento  :done, 2_1, 2026-06-22, 21d
    CLI, XL3 y expediente             :done, 2_2, after 2_1, 21d
    Tests de reglas TAN               :done, 2_3, 2026-07-13, 21d

    section F3 DSP 3P+N
    Generador de senales patron       :done, 3_1, 2026-07-06, 21d
    Clarke, PLL, H3/H5/H7             :done, 3_2, 2026-07-13, 28d
    Tests DSP y THDi academico        :done, 3_3, 2026-07-27, 21d

    section F4 Operador y SCADA
    Monitor AHF                       :done, 4_1, 2026-07-20, 28d
    Vista TAN e importacion campana   :done, 4_2, 2026-08-03, 21d
    Modbus TLS / Influx / proyecto    :done, 4_3, 2026-07-27, 28d

    section F5 SIL HIL 24 V
    FSM, E-stop e interlocks          :done, 5_1, 2026-08-10, 14d
    Vista Banco 24 V y paquete panol  :done, 5_2, 2026-08-17, 7d
    Criterios SIL y tests potencia    :done, 5_3, 2026-08-17, 7d

    section F6 Evidencias
    Regresion y casos demo            :active, 6_1, 2026-08-17, 14d
    Informe de evidencias y limites   :6_2, 2026-08-24, 7d
    Campana panol 24 V CSV            :active, 6_3, 2026-08-24, 49d

    section F7 Memoria y defensa
    Borrador de memoria P09-P12       :7_1, 2026-08-31, 28d
    PPTX y preguntas P13-P14          :7_3, 2026-09-21, 14d
    Revision del guia                 :7_2, 2026-09-28, 35d
    Guion demo live P16               :7_5, 2026-11-02, 21d
    Entrega y defensa TPA             :milestone, 7_4, 2026-12-04, 0d
```

## Hitos

| ID | Hito | Fecha | Estado |
|---|---|---|---|
| M1 | Alcance TPA congelado | 21-jun-2026 | Cumplido |
| M2 | TAN-Telecom operable | 26-jul-2026 | Cumplido |
| M3 | DSP validado con patrones | 16-ago-2026 | Cumplido |
| M4 | Plataforma de 3 vistas integrada | 21-ago-2026 | Cumplido |
| M5 | HIL SIL cerrado (sin salidas físicas) | 21-ago-2026 | Cumplido |
| M6 | Paquete de evidencias TPA | 23-ago-2026 | Cumplido |
| M7 | Borrador de memoria | 23-ago-2026 | Cumplido |
| M8 | Defensa del TPA | 04-dic-2026 | Pendiente |

## Ruta crítica

`0.1 → 0.2 → 2.1 → 3.2 → 4.1 → 5.1 → 6.1 → 7.1 → 7.4`

La ruta crítica del TPA es la cadena **problema eléctrico → señal patrón → cálculo auditable → lógica segura → evidencias → memoria**. No es el producto de 400 V. F6.3 (CSV pañol) es PLUS y no bloquea la memoria.

## Ritmo medido (21-ago-2026)

- 6 de 16 prompts (P02–P07) en **2,5 h** sin interrupciones.
- Consumo Super Grok: **3 %**. Restan P08–P16 ≈ 4–6 h y ~5 % de cuota.
- El plan semanal **no** copia ese burst: 2 sesiones/semana, 1–2 prompts.
- Holgura: paquete de software+memoria el 31-oct; defensa 04-dic-2026 (supuesto).

## Fuera de alcance

- Ensayo 380/400 VAC, 500 kW, ~700 A o banco 48 V reales
- PWM, GPIO o contactores mandados por este software
- Medición con analizador certificado / SEC
- Inyección de corriente y hard real-time

*Generado el 23-ago-2026. Autor: Andres Barbudo Rodriguez — CFT Paillaco.*
