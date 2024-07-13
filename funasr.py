import json
import websockets

import util

import asyncio
import threading
import queue


import asyncio
import threading
import queue

class FunASR:
    def __init__(self, url, on_receive):
        self.url = url
        self.on_receive = on_receive
        self.stop_event = threading.Event()
        self.send_queue = queue.Queue()
        self.thread = None
        self.ws = None

    def start(self):
        if self.thread is not None:
            self.stop()
        self.send_queue.queue.clear()
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.run_loop)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join()
            self.thread = None

    def send(self, message):
        if self.thread is None or not self.thread.is_alive():
            util.print("WebSocket is not started")
            return
        self.send_queue.put(message)

    def run_loop(self):
        async def loop():
            async with websockets.connect(self.url) as ws:
                self.ws = ws
                sender_task = asyncio.create_task(self.sender(ws))
                receiver_task = asyncio.create_task(self.receiver(ws))
                await asyncio.gather(sender_task, receiver_task)

        asyncio.run(loop())

    async def sender(self, ws):
        while not self.stop_event.is_set():
            try:
                message = await asyncio.wait_for(self.send_queue.get(), timeout=1)
                await ws.send(message)
                self.send_queue.task_done()
            except asyncio.TimeoutError:
                continue

    async def receiver(self, ws):
        while not self.stop_event.is_set():
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=1)
                meg = json.loads(message)
                text = meg["text"]
                util.print(str(meg))
                if 'mode' not in meg:
                    return
                if meg['mode'] == "2pass-offline":
                    self.on_receive(text)
            except asyncio.TimeoutError:
                continue
            except websockets.ConnectionClosed:
                break

