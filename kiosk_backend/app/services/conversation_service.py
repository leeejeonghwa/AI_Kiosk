import threading

from app.core.state_store import state_store
from ai_mod.tts_service import tts_service
from ai_mod.stt_service import STTService
from ai_mod.llm_service import LLMService

_END_KEYWORDS = [
    "아니", "없어", "없습니다", "됐어", "괜찮아", "아니요", "아니오",
    "아니에요", "그만", "됐습니다", "필요없어", "필요 없어", "없음", "안 있어",
]


class ConversationService:
    def __init__(self):
        self.running = False
        self.thread = None
        self._stt: STTService | None = None
        self._llm: LLMService | None = None
        self._injected_text: str | None = None
        self._inject_lock = threading.Lock()

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("[CONV] conversation service started")

    def stop(self):
        self.running = False
        print("[CONV] conversation service stop requested")

    def _is_end_of_conversation(self, text: str) -> bool:
        text_lower = text.strip().lower()
        return any(kw in text_lower for kw in _END_KEYWORDS)

    def inject_text(self, text: str):
        with self._inject_lock:
            self._injected_text = text
        print(f"[CONV] text injected: {text}")

    def _get_user_input(self) -> str:
        with self._inject_lock:
            if self._injected_text:
                text = self._injected_text
                self._injected_text = None
                print(f"[CONV] using injected text: {text}")
                return text
        return self._stt.transcribe(seconds=4)

    def _run(self):
        print("[CONV] conversation loop started")

        try:
            # 인사 TTS와 모델 로딩을 병렬로 실행
            model_ready = threading.Event()

            def _load_models():
                try:
                    if self._stt is None:
                        self._stt = STTService()
                    if self._llm is None:
                        self._llm = LLMService()
                    print("[CONV] 모델 로딩 완료")
                except Exception as e:
                    print(f"[CONV][ERROR] 모델 로딩 실패: {e}")
                finally:
                    model_ready.set()

            threading.Thread(target=_load_models, daemon=True).start()

            # 모델 로딩 중에 인사 TTS 재생
            tts_service.speak_blocking("안녕하세요. 무엇을 도와드릴까요?")

            # 모델 로딩 완료 대기
            model_ready.wait()

            if self._stt is None or self._llm is None:
                print("[CONV][ERROR] 모델 로딩 실패로 대화 불가")
                return

            first = True
            follow_up = False

            while self.running:
                if first:
                    result = state_store.start_listening()
                    first = False
                else:
                    result = state_store.back_to_listening()

                if not result.get("success"):
                    print(f"[CONV] state transition to LISTENING failed: {result}")
                    break

                if not self.running:
                    break

                print("[CONV] waiting for user input...")
                try:
                    user_text = self._get_user_input()
                except Exception as e:
                    print(f"[CONV][ERROR] STT 실패: {e}")
                    user_text = ""

                print(f"[CONV] user input: '{user_text}'")

                if not self.running:
                    break

                if not user_text:
                    continue

                if follow_up and self._is_end_of_conversation(user_text):
                    print("[CONV] 대화 종료 감지")
                    tts_service.speak_blocking("안녕히 가세요.")
                    self.stop()
                    state_store.reset()
                    break

                state_store.start_processing(user_text)

                llm_result = [None]
                llm_done = threading.Event()

                def _run_llm():
                    try:
                        llm_result[0] = self._llm.generate_answer(user_text)
                    except Exception as e:
                        print(f"[CONV][ERROR] LLM 호출 실패: {e}")
                        llm_result[0] = None
                    finally:
                        llm_done.set()

                threading.Thread(target=_run_llm, daemon=True).start()
                tts_service.speak_blocking("생각중입니다. 잠시만 기다려주세요~")
                llm_done.wait()
                answer = llm_result[0]

                print(f"[CONV] LLM answer: '{answer}'")

                if not self.running:
                    break

                if answer is None:
                    tts_service.speak_blocking("죄송합니다. 다시 말씀해주시겠어요?")
                    continue

                state_store.start_responding(answer)
                tts_service.speak_blocking(answer)
                tts_service.speak_blocking("다른 질문 있으세요?")
                follow_up = True

        except Exception as e:
            print(f"[CONV][ERROR] conversation loop 예외 발생: {e}")
            import traceback
            traceback.print_exc()

        print("[CONV] conversation loop ended")


conversation_service = ConversationService()
