# 3. Arquitectura del software de borde

**Autor:** Andres Barbudo Rodriguez  
**Institución:** CFT Paillaco

La defensa de **este** TPA no usa Docker. Se sostiene con:

```bash
python hil_app.py
```

y el navegador en http://localhost:8080 (Monitor AHF, Diseño TAN, Banco
24 V). `main_industrial.py` levanta el stack largo (DAQ, DSP, supervisory,
Modbus TLS, Influx). Eso es **capacidad**, no requisito.

## Tres procesos (stack industrial, opcional)

El README lo describe así:

1. **DAQ / generador de señales** — hardware o patrón sintético hacia
   memoria compartida (`SharedMemory`).
2. **DSP por microbloques** — 12,8 kHz, bloques de 128; Clarke αβ0, PLL,
   H3/H5/H7; telemetría a una cola. Un proyecto común (`/api/project`)
   comparte THDi, TAN y fallas del banco.
3. **Supervisory** — WebSocket, Influx, Modbus TCP/TLS.

```text
DAQ / patrón  →  SharedMemory  →  DSP (αβ0, PLL, H3/H5/H7)
                                        ↓
                                 cola de telemetría
                                        ↓
                              supervisory / hil_app.py
                              Monitor · TAN · Banco 24 V
```

Python sobre un SO general **no** garantiza hard real-time (frase del
README). El procesamiento es por microbloques; no se afirma ciclo
industrial cerrado.

`hil_app.py` es el recorte HIL: misma UI, sin Modbus ni Influx. El banco
es simulación (`physical_outputs_available = false`) y no conmuta la
KPS305D.

---

*Andres Barbudo Rodriguez — CFT Paillaco*
