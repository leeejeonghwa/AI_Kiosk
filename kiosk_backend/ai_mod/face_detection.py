import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import (
    MODEL_PATH,
    MIN_DETECTION_CONFIDENCE,
    MIN_SUPPRESSION_THRESHOLD,
)

FRONTAL_HOLD_SECONDS = 1.0


class LiveFaceDetector:
    def __init__(self, tts_service=None):
        self.detector = None
        self.latest_result = None

        self.frontal_start_time = None
        self.has_announced = False
        self.was_frontal = False

        self.tts_service = tts_service

    def _result_callback(self, result, output_image, timestamp_ms: int):
        self.latest_result = result

        if not result or not result.detections:
            self.reset_frontal_state()
            return

        best_detection = result.detections[0]
        is_frontal = self.is_frontal_face(best_detection)

        if is_frontal:
            # 방금 정면 상태로 진입한 경우
            if not self.was_frontal:
                self.frontal_start_time = time.time()
                self.has_announced = False
                self.was_frontal = True
                print("[상태] 정면 진입")

            elapsed = time.time() - self.frontal_start_time

            if elapsed >= FRONTAL_HOLD_SECONDS and not self.has_announced:
                message = "안녕하세요. 질문 있으세요?"
                print(message)

                if self.tts_service is not None:
                    self.tts_service.speak_async(message)

                self.has_announced = True

        else:
            if self.was_frontal:
                print("[상태] 정면 해제 -> 초기화")
            self.reset_frontal_state()

    def reset_frontal_state(self):
        self.frontal_start_time = None
        self.has_announced = False
        self.was_frontal = False

    def create(self):
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.FaceDetectorOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            result_callback=self._result_callback,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_suppression_threshold=MIN_SUPPRESSION_THRESHOLD,
        )
        self.detector = vision.FaceDetector.create_from_options(options)

    def detect_async(self, frame_bgr, timestamp_ms: int):
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        self.detector.detect_async(mp_image, timestamp_ms)

    def is_frontal_face(self, detection) -> bool:
        if not detection.categories:
            return False

        score = detection.categories[0].score
        if score < 0.5:
            return False

        bbox = detection.bounding_box
        if bbox.width < 80 or bbox.height < 80:
            return False

        keypoints = detection.keypoints
        if keypoints is None or len(keypoints) < 4:
            return False

        left_eye = keypoints[0]
        right_eye = keypoints[1]
        nose = keypoints[2]
        mouth = keypoints[3]

        eye_center_x = (left_eye.x + right_eye.x) / 2.0
        nose_eye_offset = abs(nose.x - eye_center_x)
        mouth_below_nose = mouth.y > nose.y
        eye_distance = abs(right_eye.x - left_eye.x)
        eye_y_diff = abs(right_eye.y - left_eye.y)

        # 조금 더 엄격하게
        if nose_eye_offset > 0.04:
            return False

        if not mouth_below_nose:
            return False

        if eye_distance < 0.06:
            return False

        if eye_y_diff > 0.025:
            return False

        return True

    def draw(self, frame_bgr):
        if not self.latest_result or not self.latest_result.detections:
            return frame_bgr

        for detection in self.latest_result.detections:
            bbox = detection.bounding_box
            x, y = int(bbox.origin_x), int(bbox.origin_y)
            w, h = int(bbox.width), int(bbox.height)

            cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)

            frontal = self.is_frontal_face(detection)
            text = "FRONTAL" if frontal else "NOT FRONTAL"

            cv2.putText(
                frame_bgr,
                text,
                (x, max(30, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0) if frontal else (0, 0, 255),
                2
            )

            if detection.keypoints:
                h_img, w_img, _ = frame_bgr.shape
                for kp in detection.keypoints[:4]:
                    px = int(kp.x * w_img)
                    py = int(kp.y * h_img)
                    cv2.circle(frame_bgr, (px, py), 4, (255, 0, 0), -1)

        return frame_bgr

    def close(self):
        if self.detector is not None:
            self.detector.close()
            self.detector = None