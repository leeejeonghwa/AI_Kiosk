from fastapi import FastAPI
from app.api.routes import detection, state, session,greeting,listening
from fastapi.responses import FileResponse
from pathlib import Path


app = FastAPI(title="AI Kiosk Backend")

app.include_router(detection.router, prefix="/api")
app.include_router(state.router, prefix="/api")
app.include_router(session.router, prefix="/api")
app.include_router(greeting.router, prefix="/api")
app.include_router(listening.router, prefix="/api")

@app.get("/api/health")
def health():
    return {"status": "ok"} 

@app.get("/ui")
def ui():
    return FileResponse(Path("app/test_ui/index.html"))