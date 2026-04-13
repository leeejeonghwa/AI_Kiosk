from fastapi import APIRouter
from app.services.detection_service import reset_state

router = APIRouter()

@router.post("/session/reset")
def reset_session():
    return reset_state()