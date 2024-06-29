import threading

from eff_word_net import util


class BufferedStream:
    def __init__(self, stream, chunk_size: int=1024, max_buffer_size: int=8192 * 16000):
        self.chunk_size = chunk_size
        self.max_buffer_size = max_buffer_size
        self.stream = stream
        self.buffer = bytearray()
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
                self.buffer.extend(chunk)
                if len(self.buffer) > self.max_buffer_size:
                    self.buffer = self.buffer[-self.max_buffer_size:]
                self.condition.notify_all()

    def read(self, size: int):
        with self.condition:
            while len(self.buffer) < size and not self.is_stopped:
                self.condition.wait()

            if self.is_stopped:
                return None
            chunk = self.buffer[:size]
            del self.buffer[:size]
            # util.print(str(type(chunk)))
            # util.print(str(len(chunk)))
            return bytes(chunk)

    def stop_stream(self):
        self.is_stopped = True
        with self.condition:
            self.condition.notify_all()
