# import os
# import sys
# import time
# import cv2

# from kiosk_backend.kiosk_ai.config import MODEL_PATH, CAMERA_INDEX, WINDOW_NAME, EXIT_KEY
# from kiosk_backend.kiosk_ai.face_detection import LiveFaceDetector


# def main():
#     if not os.path.exists(MODEL_PATH):
#         print(f"[오류] 모델 파일이 없습니다: {MODEL_PATH}")
#         sys.exit(1)

#     cap = cv2.VideoCapture(CAMERA_INDEX)
#     if not cap.isOpened():
#         print("[오류] 웹캠을 열 수 없습니다.")
#         sys.exit(1)

#     detector = LiveFaceDetector()
#     detector.create()

#     print("[시작] 웹캠 얼굴 감지 시작")
#     print(f"[종료] '{EXIT_KEY}' 키를 누르세요.")

#     try:
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 print("[경고] 프레임 읽기 실패")
#                 break

#             timestamp_ms = int(time.time() * 1000)
#             detector.detect_async(frame, timestamp_ms)

#             output = detector.draw(frame.copy())
#             cv2.imshow(WINDOW_NAME, output)

#             if cv2.waitKey(1) & 0xFF == ord(EXIT_KEY):
#                 break

#     finally:
#         detector.close()
#         cap.release()
#         cv2.destroyAllWindows()


# if __name__ == "__main__":
#     main()