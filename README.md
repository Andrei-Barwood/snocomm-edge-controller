# AHF Edge Controller Industrial

**Proyecto**: Controlador de Borde para Filtro Activo de Armónicos (AHF)
**Tipo**: Open Source
**Licencia**: MIT
**Propietario**: snocomm (prohibido venderlo)
**Autor**: ਕਿਰਤਅਨ ਤੈਗ ਸਿਨਗਹ (Kirtan Teg Singh)

Este repositorio es la plataforma académica del TPA: preingeniería de tableros BT, DSP 3P+N sobre señales patrón y validación SIL de un banco de **24 V**. Hoy calcula y simula; no mide con instrumento certificado ni inyecta corriente.

El alcance congelado del TPA (autor único **Andres Barbudo Rodriguez**, CFT Paillaco) está en `docs/ALCANCE_TPA_CFT_PAILLACO.md` y prima sobre esta portada. Banco físico y modelo HIL son **24 VDC / 120 W**, alineados a la wanptek KPS305D (0–30 V / 0–5 A). 48 V no cabe en esa fuente y está fuera del TPA. Fuera de alcance también: 380/400 VAC, 500 kW y ~700 A.

El DSP usa Clarke αβ0, PLL sobre tensión del PCC y extracción por secuencia (H3 cero, H5 negativa, H7 positiva). El procesamiento es por microbloques a 12.8 kHz; Python sobre un SO general **no** garantiza hard real-time.

## Características

- **DSP 3P+N por microbloques**: 7 canales (Ia Ib Ic In Va Vb Vc), SRF-PLL a tensión, THDi = Ih/I1, tests contra señales patrón en `tests/test_dsp.py`.
- **Dockerización Completa**: Preparado para hardware de borde industrial. Usa `docker-compose` para aislar y desplegar automáticamente la capa matemática, la interfaz de red y la base de datos de tiempo real.
- **Abstracción de ADC Físico**: Interfaz `adc_hardware_driver.py` construida para leer de buses industriales o sistemas DAQ físicos, compartiendo datos de alta velocidad con el controlador mediante *multiprocessing shared memory*.
- **Telemetría SCADA y Modbus TLS**: Actúa como servidor para cualquier SCADA de planta, inyectando métricas complejas (THDi, Saturación, Frecuencia) mediante un puente a **InfluxDB** y exponiendo variables de retención en **Modbus Secure (TLS)**, protegiendo las redes de Tecnología Operativa (OT).
- **Dashboard de Operador Nativo**: Interfaz web integrada (HTML/JS + WebSockets) estilizada con la paleta corporativa para monitorear formas de onda en tiempo real, latencias de DSP y métricas clave en el puerto 8080.
- **Diseño TAN-Telecom Integrado**: El mismo dashboard incorpora el predimensionamiento IEC 61439 de tableros para nodos de telecomunicaciones, con cálculo de corriente, Icc/Icw, calentamiento, envolvente XL³ y forma de separación.

## Arquitectura de Procesos (IPC)

El sistema levanta 3 procesos asíncronos en el sistema operativo:
1. **DAQ / Signal Generator**: Lee buffers del hardware físico (o genera señales sintéticas con deriva de frecuencia y contaminación) e inyecta matrices Numpy en Memoria Compartida (`SharedMemory`).
2. **DSP por microbloques**: Lee de la memoria compartida, extrae I1/H3/H5/H7 con el modelo αβ0 y emite telemetría a una cola. Un proyecto común (`/api/project`) comparte THDi, prediseño TAN y fallas del banco.
3. **Supervisory Process (TS)**: Consume la cola, gestiona clientes WebSocket, inyecta registros a la serie de tiempo InfluxDB y mantiene el Servidor Modbus TCP/TLS.

## Requisitos de Instalación

- **Entorno**: Linux Industrial, IPC, Raspberry Pi, macOS o Windows (WSL2 recomendado).
- **Herramientas**: Docker y Docker Compose (Opcional, pero recomendado para despliegue). Python 3.11+.

## Despliegue con Docker (Recomendado)

El sistema viene empaquetado para levantar el controlador y la base de datos InfluxDB de manera inmediata.

1. (Opcional) Edita `config_industrial.yaml` para habilitar `mode: hardware` si tienes DAQ físico, o cambia los puertos Modbus y certificados TLS.
2. Construye y despliega usando docker-compose:
```bash
docker-compose up --build
```
3. Accede al Dashboard del operador abriendo tu navegador web en: `http://localhost:8080`

La navegación superior reúne ambos flujos: **Monitor AHF** para operación en vivo y **Diseño TAN** para ingeniería del tablero.

La tercera vista, **Banco 24V**, incorpora el prototipo HIL de la misma
clase de tensión que el pañol: autoprueba, precarga lógica, E-stop,
inyección de fallas y rearme enclavado. Esta función es simulación
(`physical_outputs_available = false`) y no conmuta la KPS305D.

La arquitectura y los criterios de avance están documentados en
`docs/POWER_STAGE_24V.md` y `docs/BANCO_FISICO_24V.md`.

Para probar únicamente el banco HIL, sin iniciar Modbus, InfluxDB ni hardware:

```bash
python hil_app.py
```

Luego abre `http://localhost:8080` y selecciona **Banco 24V**.

## Ejecución Local (Sin Docker)

Si prefieres ejecutar el código desnudo sobre Python:

```bash
# Crear entorno virtual e instalar requerimientos
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements_pro.txt

# Generar certificados autofirmados (para Modbus TLS)
./generate_certs.sh

# Arrancar el orquestador
python main_industrial.py
```

## Credenciales por Defecto de InfluxDB
Si usas Docker, el servidor de InfluxDB auto-creará un bucket para el archivo histórico del filtro:
- **Puerto**: `8086`
- **Organización**: `snocomm`
- **Bucket**: `telemetry`
- **Token Admin**: `my-super-secret-auth-token` (Configurado en el docker-compose)

---
*Plataforma TPA: problema eléctrico → señal patrón → cálculo auditable → lógica segura → banco 24 V (KPS305D + Gratten GA1102CAL).*
