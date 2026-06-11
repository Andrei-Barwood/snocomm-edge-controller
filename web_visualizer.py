import asyncio
import logging
import uvicorn
import webbrowser
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import main as controller_main
import mock_scada_server

# Configuración de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web_visualizer")

app = FastAPI()

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_index():
    return FileResponse("templates/index.html")

# Cola asíncrona para comunicar el lazo de control con los websockets
data_queue = asyncio.Queue(maxsize=5)

# Lista de clientes conectados
connected_clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            # Mantener la conexión abierta
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def broadcast_data():
    """Lee datos de la cola y los envía a todos los clientes conectados."""
    while True:
        data = await data_queue.get()
        if not connected_clients:
            continue
        
        # Eliminar clientes desconectados que hayan quedado
        disconnected = []
        for client in connected_clients:
            try:
                await client.send_json(data)
            except Exception:
                disconnected.append(client)
        
        for client in disconnected:
            connected_clients.remove(client)

async def start_services():
    """Inicia el mock scada, el lazo de control y el broadcast de websockets."""
    logger.info("Iniciando servicios del simulador...")
    
    # Arrancar Mock SCADA Server
    asyncio.create_task(mock_scada_server.run_server())
    
    # Darle un momento al mock para arrancar
    await asyncio.sleep(1.0)
    
    # Arrancar el loop principal del controlador, pasándole la cola
    asyncio.create_task(controller_main.main(data_queue=data_queue))
    
    # Arrancar el broadcast de websockets
    asyncio.create_task(broadcast_data())
    
    # Abrir el navegador automáticamente
    webbrowser.open("http://localhost:8080")

@app.on_event("startup")
async def startup_event():
    await start_services()

if __name__ == "__main__":
    logger.info("Iniciando Web Visualizer en http://localhost:8080")
    uvicorn.run("web_visualizer:app", host="0.0.0.0", port=8080, log_level="info")
