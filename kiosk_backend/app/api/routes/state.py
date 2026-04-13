from fastapi import APIRouter
from app.services.detection_service import get_current_state

router = APIRouter()

@router.get("/state")
def read_state():
    return get_current_state()