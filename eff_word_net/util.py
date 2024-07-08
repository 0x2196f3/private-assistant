import asyncio
import queue
import sys
import threading

from eff_word_net.audio_processing import MODEL_TYPE_MAPPER


def print(text: str):
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


class ThreadLooper:
    def __init__(self):
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.loop = asyncio.get_event_loop()

    def run_on_main_thread(self, func, **args):
        with self.lock:
            self.queue.put((func, args))

    def start(self):
        while True:
            try:
                func, args, kwargs = self.queue.get(block=True, timeout=1)
                if asyncio.iscoroutinefunction(func):
                    self.loop.run_until_complete(func(args, kwargs))
                else:
                    func(*args, **kwargs)
            except queue.Empty:
                pass


threadLooper = ThreadLooper()


def create_model(model_name: str) -> object:
    if model_name in MODEL_TYPE_MAPPER:
        return MODEL_TYPE_MAPPER[model_name](use_quantized_model=True)
    else:
        raise ValueError(f"Invalid model name: {model_name}")
