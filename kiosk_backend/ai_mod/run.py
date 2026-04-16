import os
import sys
import time
import cv2

from config import MODEL_PATH, CAMERA_INDEX, WINDOW_NAME, EXIT_KEY
from face_detection import LiveFaceDetector
from tts_service import TTSService
from stt_service import STTService


def main():
    if not os.path.exists(MODEL_PATH):
        print(f"[오류] 모델 파일이 없습니다: {MODEL_PATH}")
        sys.exit(1)

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("[오류] 웹캠을 열 수 없습니다.")
        sys.exit(1)

    tts_service = TTSService()
    stt_service = STTService()
    detector = LiveFaceDetector(tts_service=tts_service)
    detector.create()

    print("[시작] 웹캠 얼굴 감지 시작")
    print(f"[종료] '{EXIT_KEY}' 키를 누르세요.")
    print("[STT] 's' 키를 누르면 4초 동안 음성을 녹음하고 텍스트로 변환합니다.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[경고] 프레임 읽기 실패")
                break

            timestamp_ms = int(time.time() * 1000)
            detector.detect_async(frame, timestamp_ms)

            output = detector.draw(frame.copy())
            cv2.imshow(WINDOW_NAME, output)

            key = cv2.waitKey(1) & 0xFF

            if key == ord(EXIT_KEY):
                break

            if key == ord("s"):
                print("[STT] 음성 인식을 시작합니다.")
                text = stt_service.transcribe(seconds=4)

                if text:
                    print(f"[STT 결과] {text}")
                else:
                    print("[STT 결과] 인식된 음성이 없습니다.")

    finally:
        detector.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()