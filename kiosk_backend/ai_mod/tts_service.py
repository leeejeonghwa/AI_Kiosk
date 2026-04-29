import threading
import pyttsx3


class TTSService:
    def __init__(self, rate: int = 175, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self.is_speaking = False
        self.lock = threading.Lock()

    def _get_korean_voice(self, engine):
        try:
            voices = engine.getProperty("voices")
            for voice in voices:
                name = getattr(voice, "name", "")
                if "Korean" in name or "Heami" in name or "한국어" in name:
                    return voice.id
        except Exception:
            pass
        return None

    def _synthesize_and_play(self, text: str):
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            voice_id = self._get_korean_voice(engine)
            if voice_id:
                engine.setProperty("voice", voice_id)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[TTS 오류] {e}")

    def speak_async(self, text: str):
        with self.lock:
            if self.is_speaking:
                return
            self.is_speaking = True

        def _run():
            try:
                self._synthesize_and_play(text)
            finally:
                with self.lock:
                    self.is_speaking = False

        threading.Thread(target=_run, daemon=True).start()

    def speak_blocking(self, text: str):
        with self.lock:
            if self.is_speaking:
                return
            self.is_speaking = True

        done = threading.Event()

        def _run():
            try:
                self._synthesize_and_play(text)
            finally:
                with self.lock:
                    self.is_speaking = False
                done.set()

        threading.Thread(target=_run, daemon=True).start()
        done.wait()


tts_service = TTSService()
