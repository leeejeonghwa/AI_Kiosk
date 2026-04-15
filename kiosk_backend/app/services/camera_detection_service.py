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

        self.cooldown_seconds = 5.0
        self.last_trigger_time = 0.0

    def start(self) -> None:
        if self.running:
            print("[INFO] CameraDetectionService already running")
            return

        print(f"[INFO] opening camera index={CAMERA_INDEX}")

        # Windows에서는 CAP_DSHOW가 안정적인 편
        self.cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            print(f"[ERROR] 웹캠을 열 수 없습니다. camera_index={CAMERA_INDEX}")
            self.cap = None
            return

        print("[INFO] camera opened successfully")

        try:
            self.detector = LiveFaceDetector()
            self.detector.create()
            print("[INFO] detector created successfully")
        except Exception as e:
            print(f"[ERROR] detector create failed: {e}")
            if self.cap:
                self.cap.release()
                self.cap = None
            return

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
        print("[INFO] camera loop started")

        while self.running:
            if self.cap is None or self.detector is None:
                time.sleep(0.1)
                continue

            ret, frame = self.cap.read()
            if not ret:
                print("[WARN] frame read failed")
                time.sleep(0.05)
                continue

            timestamp_ms = int(time.time() * 1000)

            try:
                self.detector.detect_async(frame, timestamp_ms)
            except Exception as e:
                print(f"[ERROR] detect_async failed: {e}")
                time.sleep(0.1)
                continue

            # 정면 얼굴 1초 유지 -> 인사 시작
            if self.detector.consume_greeting_trigger():
                print("[INFO] greeting trigger detected")
                self._handle_detected_user()

            # 얼굴이 일정 시간 사라짐 -> IDLE 복귀
            if self.detector.consume_no_face_trigger():
                print("[INFO] no face trigger detected")
                self._handle_no_face()

            time.sleep(0.03)

    def _handle_detected_user(self) -> None:
        now = time.time()

        if now - self.last_trigger_time < self.cooldown_seconds:
            print("[INFO] trigger ignored by cooldown")
            return

        current = state_store.get_state()
        current_state = current.get("current_state")
        print(f"[INFO] current_state={current_state}")

        if current_state != "IDLE":
            print("[INFO] trigger ignored because state is not IDLE")
            return

        detection_result = state_store.handle_detection(detected=True)
        print(f"[INFO] detection_result={detection_result}")

        if detection_result.get("state") == "USER_DETECTED":
            greeting_result = state_store.start_greeting()
            self.last_trigger_time = now

            print(
                "[INFO] Greeting started | "
                f"session_id={greeting_result.get('session_id')} | "
                f"message={greeting_result.get('message_text')}"
            )

    def _handle_no_face(self) -> None:
        current = state_store.get_state()
        current_state = current.get("current_state")
        print(f"[INFO] no face current_state={current_state}")

        if current_state in ["USER_DETECTED", "GREETING", "LISTENING"]:
            reset_result = state_store.reset()
            print(f"[INFO] no face detected -> reset to IDLE | result={reset_result}")


camera_detection_service = CameraDetectionService()