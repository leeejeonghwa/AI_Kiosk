import asyncio
import os
import tempfile
import threading

import edge_tts
import pygame

VOICE = "ko-KR-SunHiNeural"
PITCH = "+15Hz"
RATE = "+10%"

pygame.mixer.init()


class TTSService:
    def __init__(self, voice: str = VOICE, pitch: str = PITCH, rate: str = RATE):
        self.voice = voice
        self.pitch = pitch
        self.rate = rate
        self.is_speaking = False
        self.lock = threading.Lock()

    def _synthesize_and_play(self, text: str):
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp_path = f.name

            asyncio.run(edge_tts.Communicate(text, self.voice, pitch=self.pitch, rate=self.rate).save(tmp_path))

            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(50)
        except Exception as e:
            print(f"[TTS 오류] {e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

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
