from fastapi import APIRouter
from app.services.greeting_service import start_greeting

router = APIRouter()

@router.post("/greeting")
def greeting():
    return start_greeting()