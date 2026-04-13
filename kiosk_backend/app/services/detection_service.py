from pydantic import BaseModel
from app.core.state_store import state_store


class DetectionRequest(BaseModel):
    detected: bool


def process_detection(request: DetectionRequest) -> dict:
    return state_store.handle_detection(detected=request.detected)


def get_current_state() -> dict:
    return state_store.get_state()


def reset_state() -> dict:
    return state_store.reset()