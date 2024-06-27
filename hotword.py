import asyncio
import threading

from eff_word_net.engine import HotwordDetector
from eff_word_net.streams import SimpleMicStream


class Listener:
    def __init__(self, detector: HotwordDetector, mic_stream: SimpleMicStream, on_detect):
        self.listener_thread = None
        self.detector = detector
        self.mic_stream = mic_stream
        self.on_detect = on_detect

    def start(self):
        self.listener_thread = threading.Thread(target=self._start_listening_thread)
        self.listener_thread.start()

    def _start_listening_thread(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._start_listening())
        loop.close()

    def stop(self):
        if self.listener_thread:
            self.listener_thread.do_run = False
            try:
                self.listener_thread.join()
            except Exception:
                pass
            self.listener_thread = None

    async def _start_listening(self):
        mic_stream = self.mic_stream
        mic_stream.start_stream()
        hw = self.detector
        while True:
            frame = mic_stream.getFrame()
            result = hw.scoreFrame(frame)
            if result is None:
                continue
            if (result["match"]):
                await self.on_detect(mic_stream)

