"""Standalone dashboard for safe HIL testing without SCADA or power hardware."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from acquisition_service import router as acquisition_router
from calculator_service import router as calculator_router
from power_stage_service import router as power_stage_router
from project_service import router as project_router
from project_store import store
from tan_service import router as tan_router


app = FastAPI(title="Snocomm 24 V HIL")
app.include_router(power_stage_router)
app.include_router(tan_router)
app.include_router(project_router)
app.include_router(acquisition_router)
app.include_router(calculator_router)
store.configure("hil", "none", "hil_simulation")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("templates/index.html")


@app.websocket("/ws")
async def idle_telemetry_channel(websocket: WebSocket):
    """Keep the dashboard telemetry channel valid while testing HIL only."""
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        return


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
