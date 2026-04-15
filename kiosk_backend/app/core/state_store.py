from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass
class KioskState:
    current_state: str = "IDLE"
    session_id: Optional[str] = None
    greeted: bool = False
    last_detected_at: Optional[str] = None


class StateStore:
    def __init__(self) -> None:
        self._state = KioskState()

    def get_state(self) -> dict:
        return asdict(self._state)

    def handle_detection(self, detected: bool) -> dict:
        now = datetime.now().isoformat(timespec="seconds")

        if not detected:
            return {
                "success": True,
                "message": "no user detected",
                "state": self._state.current_state,
                "session_id": self._state.session_id,
            }

        if self._state.current_state == "IDLE":
            self._state.current_state = "USER_DETECTED"
            self._state.session_id = str(uuid4())
            self._state.greeted = False
            self._state.last_detected_at = now

            return {
                "success": True,
                "message": "user detected, state changed",
                "state": self._state.current_state,
                "session_id": self._state.session_id,
                "last_detected_at": self._state.last_detected_at,
            }

        self._state.last_detected_at = now
        return {
            "success": True,
            "message": "user already detected",
            "state": self._state.current_state,
            "session_id": self._state.session_id,
            "last_detected_at": self._state.last_detected_at,
        }

    def start_greeting(self) -> dict:
        if self._state.current_state not in ["USER_DETECTED", "GREETING"]:
            return {
                "success": False,
                "message": "greeting cannot start in current state",
                "state": self._state.current_state,
                "session_id": self._state.session_id,
            }

        self._state.current_state = "GREETING"
        self._state.greeted = True

        return {
            "success": True,
            "message": "greeting started",
            "state": self._state.current_state,
            "session_id": self._state.session_id,
            "message_text": "안녕하세요. 무엇을 도와드릴까요?",
            "tts_text": "안녕하세요. 무엇을 도와드릴까요?"
        }
    
    def start_listening(self) -> dict:
        if self._state.current_state != "GREETING":
            return {
            "success": False,
            "message": "cannot start listening in current state",
            "state": self._state.current_state,
        }

        self._state.current_state = "LISTENING"

        return {
        "success": True,
        "message": "listening started",
        "state": self._state.current_state,
        "session_id": self._state.session_id
    }

    def reset(self) -> dict:
        self._state = KioskState()
        return {
            "success": True,
            "message": "state reset completed",
            "state": self._state.current_state,
        }


state_store = StateStore()