import queue
import threading

import queue
import threading
import signal


class MainThreadLooper:
    def __init__(self):
        self.queue = queue.Queue()

    def send(self, func, *args, **kwargs):
        self.queue.put((func, args, kwargs))

    def loop(self):
        while True:
            try:
                func, args, kwargs = self.queue.get(block=True)
                if args and kwargs:
                    func(*args, **kwargs)  # Call instance method with self implicit, args, and kwargs
                elif args and not kwargs:
                    func(*args)  # Call instance method with self implicit and args
                elif not args and kwargs:
                    func(**kwargs)  # Call instance method with self implicit and kwargs
                else:
                    func()
            except KeyboardInterrupt:
                break

    def run(self):
        signal.signal(signal.SIGINT, signal.default_int_handler)
        self.loop()


if __name__ == "__main__":
    looper = MainThreadLooper()


    def my_function(arg1, arg2, kwarg1=None):
        print(f"Executing my_function with args {arg1}, {arg2} and kwargs {kwarg1}")


    looper.send(my_function, 1, 2, kwarg1="hello")

    looper.run()
