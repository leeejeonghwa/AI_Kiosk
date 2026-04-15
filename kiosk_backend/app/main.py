from fastapi import FastAPI
from app.api.routes import detection, state, session,greeting,listening

app = FastAPI(title="AI Kiosk Backend")

app.include_router(detection.router, prefix="/api")
app.include_router(state.router, prefix="/api")
app.include_router(session.router, prefix="/api")
app.include_router(greeting.router, prefix="/api")
app.include_router(listening.router, prefix="/api")

@app.get("/api/health")
def health():
    return {"status": "ok"} 