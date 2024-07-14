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
        self.send_queue = None
        self.thread = None
        self.loop = None

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

    def send(self, message):
        if self.thread is None:
            util.log("WebSocket is not started")
            return
        self.loop.create_task(self._send(message))

    async def _send(self, message):
        await self.send_queue.put(message)

    def run_loop(self):
        async def loop():
            self.send_queue = asyncio.Queue()
            if self.url.startswith("wss://"):
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            else:
                ssl_context = None

            async with websockets.connect(self.url, ssl=ssl_context) as ws:
                receiver_task = asyncio.create_task(self.receiver(ws))
                sender_task = asyncio.create_task(self.sender(ws))
                await asyncio.gather(receiver_task, sender_task)

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(loop())

    async def sender(self, ws):
        while not self.stop_event.is_set():
            try:
                message = await asyncio.wait_for(self.send_queue.get(), timeout=0.1)
                await ws.send(message)
                self.send_queue.task_done()
            except asyncio.TimeoutError:
                continue

    async def receiver(self, ws):
        while not self.stop_event.is_set():
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=0.1)
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
