"""
Project: AHF Edge Controller
Type: Open Source
License: MIT
Owner: snocomm (prohibido venderlo)
Author: ਕਿਰਤਅਨ ਤੈਗ ਸਿਨਗਹ (Kirtan Teg Singh)
"""
import asyncio
import logging
import uvicorn
import webbrowser
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pymodbus.server import StartAsyncTcpServer, StartAsyncTlsServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext, ModbusSlaveContext
from tan_service import router as tan_router
from power_stage_service import router as power_stage_router
from project_service import router as project_router
from acquisition_service import router as acquisition_router
from calculator_service import router as calculator_router
from project_store import store

logger = logging.getLogger("Supervisory")

app = FastAPI()
app.include_router(tan_router)
app.include_router(power_stage_router)
app.include_router(project_router)
app.include_router(acquisition_router)
app.include_router(calculator_router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_index():
    return FileResponse("templates/index.html")

# Globals for the FastAPI app
connected_clients = []
telemetry_queue = None
config = None
influx_client = None
influx_write_api = None
modbus_store = None
async_queue = None
tq_global = None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def telemetry_broadcaster():
    """Reads from telemetry queue, updates Modbus, InfluxDB, and WebSockets."""
    global telemetry_queue, influx_write_api, config, modbus_store
    
    last_influx_time = time.time()
    
    while True:
        try:
            data = await asyncio.wait_for(telemetry_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            continue

        # 1. Update Modbus Registers (Registers 0-10)
        # Using a simple integer scaling for float values
        if modbus_store is not None:
            store.update_monitor(data)
            modbus_store.setValues(3, 0, [
                int(data.get('thdi', 0) * 10),
                int(data.get('freq_est', 0) * 100),
                int(data.get('h3_rms', 0) * 10),
                int(data.get('h5_rms', 0) * 10),
                int(data.get('h7_rms', 0) * 10),
                1 if data.get('is_saturated') else 0,
                int(data.get('i1_rms', 0) * 10),
                int(data.get('in_rms', 0) * 10),
            ])
            
        # 2. Update WebSocket clients
        if connected_clients:
            disconnected = []
            for client in connected_clients:
                try:
                    await client.send_json(data)
                except Exception:
                    disconnected.append(client)
            for client in disconnected:
                connected_clients.remove(client)
                
        # 3. Push to InfluxDB periodically (e.g., every 1 second)
        now = time.time()
        if influx_write_api is not None and (now - last_influx_time) >= 1.0:
            last_influx_time = now
            try:
                p = Point("power_quality") \
                    .tag("controller_id", "edge_01") \
                    .field("thdi", float(data['thdi'])) \
                    .field("freq_est", float(data['freq_est'])) \
                    .field("h3_rms", float(data['h3_rms'])) \
                    .field("h5_rms", float(data['h5_rms'])) \
                    .field("h7_rms", float(data.get('h7_rms', 0))) \
                    .field("i1_rms", float(data.get('i1_rms', 0))) \
                    .field("in_rms", float(data.get('in_rms', 0))) \
                    .field("is_saturated", bool(data.get('is_saturated'))) \
                    .field("t_dsp_ms", float(data.get('t_dsp_ms', 0)))
                influx_write_api.write(bucket=config['influxdb']['bucket'], record=p)
            except Exception as e:
                logger.error(f"InfluxDB write error: {e}")

async def run_modbus_server(cfg):
    global modbus_store
    
    tls_config = cfg['scada'].get('tls', {})
    use_tls = tls_config.get('enabled', False)
    
    port = tls_config.get('port', 8020) if use_tls else cfg['scada']['port']
    protocol = "TLS" if use_tls else "TCP"
    
    logger.info(f"Starting Modbus {protocol} Supervisory Server on {cfg['scada']['host']}:{port}")
    
    datablock = ModbusSequentialDataBlock(0, [0] * 100)
    modbus_store = ModbusSlaveContext(di=datablock, co=datablock, hr=datablock, ir=datablock, zero_mode=True)
    context = ModbusServerContext(slaves={cfg['scada']['unit_id']: modbus_store}, single=False)
    
    if use_tls:
        import ssl
        sslctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        sslctx.load_cert_chain(certfile=tls_config['certfile'], keyfile=tls_config['keyfile'])
        
        await StartAsyncTlsServer(
            context=context,
            address=(cfg['scada']['host'], port),
            sslctx=sslctx
        )
    else:
        await StartAsyncTcpServer(
            context=context,
            address=(cfg['scada']['host'], port)
        )

async def start_services():
    logger.info("Starting TS Services...")
    # Setup InfluxDB
    global influx_client, influx_write_api
    influx_client = InfluxDBClient(url=config['influxdb']['url'], token=config['influxdb']['token'], org=config['influxdb']['org'])
    influx_write_api = influx_client.write_api(write_options=ASYNCHRONOUS)
    
    # Start Modbus Server
    asyncio.create_task(run_modbus_server(config))
    
    # Start Telemetry Broadcaster
    asyncio.create_task(telemetry_broadcaster())
    
    logger.info("Opening dashboard...")
    webbrowser.open("http://localhost:8080")

@app.on_event("startup")
async def startup_event():
    global async_queue, telemetry_queue
    import threading
    loop = asyncio.get_running_loop()
    
    # Initialize the queue in the context of the running loop
    async_queue = asyncio.Queue(maxsize=10)
    telemetry_queue = async_queue
    
    def queue_bridge():
        while True:
            try:
                data = tq_global.get()
                asyncio.run_coroutine_threadsafe(async_queue.put(data), loop)
            except Exception as e:
                pass
                
    threading.Thread(target=queue_bridge, daemon=True).start()
    await start_services()

@app.on_event("shutdown")
async def shutdown_event():
    if influx_client:
        influx_client.close()

def start_ts_process(cfg, tq):
    global config, telemetry_queue, async_queue, tq_global
    config = cfg
    tq_global = tq
    mode = cfg.get("system", {}).get("mode", "simulation")
    acquisition = "hardware_placeholder" if mode == "hardware" else "simulation"
    pattern = (cfg.get("simulation") or {}).get("pattern")
    store.configure("industrial", acquisition, "hil_simulation", pattern)
    
    # We will initialize the async queue and replace telemetry_queue with it.
    # The actual bridge thread is started in the startup_event when the loop exists.
    logger.info("Starting Web Visualizer and TS Process on http://0.0.0.0:8080")
    
    # We need to create the Queue within the event loop if possible, but asyncio.Queue
    # can be instantiated outside in older Pythons if a loop is implicitly created, 
    # but in modern Python it's safer to create it in the loop. We will just use the global scope.
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")
