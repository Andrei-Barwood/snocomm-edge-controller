# AHF Edge Controller Industrial

**Proyecto**: Controlador de Borde para Filtro Activo de Armónicos (AHF)
**Tipo**: Open Source
**Licencia**: MIT
**Propietario**: snocomm (prohibido venderlo)
**Autor**: ਕਿਰਤਅਨ ਤੈਗ ਸਿਨਗਹ (Kirtan Teg Singh)

Este repositorio contiene la arquitectura de software industrial para un Edge Controller de un Filtro Activo de Armónicos. El sistema abandona la simple transformada FFT y adopta una matemática avanzada de teoría de control en tiempo real (SRF-PLL, dq0, Clarke/Park), aislando estrictamente la lógica matemática de la supervisión SCADA mediante memoria compartida (`/dev/shm`) y subprocesos paralelos (IPC).

## Características Comerciales Integradas

- **Lazo de Control Hard Real-Time (HRT)**: Operando a una tasa de muestreo de 12.8 kHz en micro-lotes de 10ms. Realiza estimación de frecuencia, transformada de Clarke, rastreo SRF-PLL, extracción multi-SRF (dq0) de armónicos de secuencia cero, negativa y positiva, y predicción de fase.
- **Dockerización Completa**: Preparado para hardware de borde industrial. Usa `docker-compose` para aislar y desplegar automáticamente la capa matemática, la interfaz de red y la base de datos de tiempo real.
- **Abstracción de ADC Físico**: Interfaz `adc_hardware_driver.py` construida para leer de buses industriales o sistemas DAQ físicos, compartiendo datos de alta velocidad con el controlador mediante *multiprocessing shared memory*.
- **Telemetría SCADA y Modbus TLS**: Actúa como servidor para cualquier SCADA de planta, inyectando métricas complejas (THDi, Saturación, Frecuencia) mediante un puente a **InfluxDB** y exponiendo variables de retención en **Modbus Secure (TLS)**, protegiendo las redes de Tecnología Operativa (OT).
- **Dashboard de Operador Nativo**: Interfaz web integrada (HTML/JS + WebSockets) estilizada con la paleta corporativa para monitorear formas de onda en tiempo real, latencias de DSP y métricas clave en el puerto 8080.

## Arquitectura de Procesos (IPC)

El sistema levanta 3 procesos asíncronos en el sistema operativo:
1. **DAQ / Signal Generator**: Lee buffers del hardware físico (o genera señales sintéticas con deriva de frecuencia y contaminación) e inyecta matrices Numpy en Memoria Compartida (`SharedMemory`).
2. **HRT Loop (DSP)**: Lee de la memoria compartida, procesa vectores dq0, controla límites de corriente (`hardware clamping`) y emite telemetría sub-muestreada a una cola estándar (Queue).
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
*Diseñado bajo rigor matemático para la mitigación de THDi en sistemas industriales trifásicos.*
