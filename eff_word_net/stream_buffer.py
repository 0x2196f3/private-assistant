import threading
from collections import deque
import pyaudio

class MicStream:
    def __init__(self, stream, chuck_size=80, buffer_size=8192):
        self.chunk_size = chuck_size
        self.buffer_size = buffer_size
        self.stream = stream
        self.buffer = deque(maxlen=self.buffer_size)
        self.is_stopped = False
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def start_stream(self):
        self.is_stopped = False
        threading.Thread(target=self._record_loop).start()

    def _record_loop(self):
        while not self.is_stopped:
            chunk = self.stream.read(self.chunk_size, exception_on_overflow=False)
            with self.condition:
                self.buffer.append(chunk)
                self.condition.notify_all()

    def read(self, size):
        if size % self.chunk_size != 0:
            raise ValueError("Size must be a multiple of CHUNK_SIZE")
        with self.condition:
            while len(self.buffer) * self.chunk_size < size and not self.is_stopped:
                self.condition.wait()

            if self.is_stopped:
                return None
            chunks = []
            while len(chunks) * self.chunk_size < size:
                chunks.append(self.buffer.popleft())
            return b''.join(chunks)

    def stop_stream(self):
        self.is_stopped = True
        with self.condition:
            self.condition.notify_all()
