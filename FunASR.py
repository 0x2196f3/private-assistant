import json
import ssl

import websockets

import util

import asyncio
import threading


class FunASR:
    def __init__(self, url, on_receive):
        self.url = url
        self.on_receive = on_receive
        self.stop_event = threading.Event()
        self.thread = None
        self.loop = None
        self.ws = None

    def start(self):
        if self.thread is not None:
            self.stop()
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.run_loop)
        self.thread.start()

    def is_stopped(self):
        return self.thread is None

    def stop(self):
        self.stop_event.set()
        if self.thread is not None:
            if threading.current_thread() != self.thread:
                self.thread.join()
            self.thread = None

    async def send(self, message):
        if self.thread is None:
            util.log("WebSocket is not started")
            return
        self.ws.send(message)

    def run_loop(self):
        async def loop():
            self.send_queue = asyncio.Queue()
            if self.url.startswith("wss://"):
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            else:
                ssl_context = None

            async with websockets.connect(self.url, ssl=ssl_context, subprotocols=["binary"],
                                          ping_interval=None, ) as self.ws:
                while not self.stop_event.is_set():
                    try:
                        message = await self.ws.recv()
                        meg = json.loads(message)
                        if 'mode' not in meg:
                            continue
                        text = meg["text"]
                        util.log(str(meg))
                        if meg['mode'] == "2pass-offline":
                            self.on_receive(text)
                    except asyncio.TimeoutError:
                        continue
                    except websockets.ConnectionClosed:
                        break

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(loop())
