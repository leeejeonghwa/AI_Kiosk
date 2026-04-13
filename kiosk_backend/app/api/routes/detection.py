from fastapi import APIRouter
from app.services.detection_service import DetectionRequest, process_detection

router = APIRouter()

@router.post("/detection")
def detect_user(request: DetectionRequest):
    return process_detection(request)