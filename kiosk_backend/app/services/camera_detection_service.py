import time
import threading
import cv2

from app.core.state_store import state_store
from ai.config import CAMERA_INDEX
from ai.face_detection import LiveFaceDetector


class CameraDetectionService:
    def __init__(self) -> None:
        self.cap = None
        self.detector = None
        self.running = False
        self.thread = None

        # 연속 감지로 인사 반복되는 것 방지
        self.cooldown_seconds = 5.0
        self.last_trigger_time = 0.0

    def start(self) -> None:
        if self.running:
            print("[INFO] CameraDetectionService already running")
            return

        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        if not self.cap.isOpened():
            print("[ERROR] 웹캠을 열 수 없습니다.")
            self.cap = None
            return

        self.detector = LiveFaceDetector()
        self.detector.create()

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

        print("[INFO] CameraDetectionService started")

    def stop(self) -> None:
        self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

        if self.detector:
            self.detector.close()
            self.detector = None

        if self.cap:
            self.cap.release()
            self.cap = None

        print("[INFO] CameraDetectionService stopped")

    def _run_loop(self) -> None:
        while self.running:
            if self.cap is None or self.detector is None:
                time.sleep(0.1)
                continue

            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            timestamp_ms = int(time.time() * 1000)
            self.detector.detect_async(frame, timestamp_ms)

            if self.detector.consume_greeting_trigger():
                self._handle_detected_user()

            time.sleep(0.03)

    def _handle_detected_user(self) -> None:
        now = time.time()

        if now - self.last_trigger_time < self.cooldown_seconds:
            return

        current = state_store.get_state()
        current_state = current.get("current_state")

        # 광고/대기 상태일 때만 새로 진입
        if current_state != "IDLE":
            return

        detection_result = state_store.handle_detection(detected=True)

        if detection_result.get("state") == "USER_DETECTED":
            greeting_result = state_store.start_greeting()
            self.last_trigger_time = now

            print(
                "[INFO] Greeting started | "
                f"session_id={greeting_result.get('session_id')} | "
                f"message={greeting_result.get('message_text')}"
            )


camera_detection_service = CameraDetectionService()