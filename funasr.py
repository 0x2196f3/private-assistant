import json

import websocket
import threading

import util


class FunASR:
    def __init__(self, url: str, on_receive):
        self.url = url
        self.on_receive = on_receive
        self.ws = None
        self.stopped = True
        self.lock = threading.Lock()
        self.thread = None

    def connect(self):
        if self.thread:
            self.stop()
        self.thread = threading.Thread(target=self._connect)
        self.thread.daemon = True
        self.thread.start()

    def _connect(self):
        self.stopped = False
        self.ws = websocket.WebSocketApp(self.url, on_open=self.on_open, on_message=self.on_message,
                                         on_error=self.on_error, on_close=self.on_close)
        try:
            self.ws.run_forever(reconnect=5)
        except Exception as e:
            print(e)
        finally:
            self.stopped = True
            with self.lock:
                try:
                    if self.ws:
                        self.ws.close()
                except:
                    pass

    def on_open(self, ws):
        util.print("Opened connection")

    def on_message(self, ws, message):
        meg = json.loads(message)
        text = meg["text"]
        print(str(meg))
        if 'mode' not in meg:
            return
        if meg['mode'] == "2pass-offline":
            self.on_receive(text)

    def on_error(self, ws, error):
        util.print(error)

    def on_close(self, ws, close_status_code, close_msg):
        util.print("### closed ###")

    def send(self, message):
        with self.lock:
            if self.ws:
                self.ws.send(message)

    def stop(self):
        self.stopped = True
        with self.lock:
            if self.ws:
                self.ws.close()
        self.thread.join()
        self.thread = None
        self.ws = None
