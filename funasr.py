import asyncio
import random

import websockets
import ssl
import json
import numpy as np
import threading

from eff_word_net import util


class FunASR:
    def __init__(self, url: str, on_receive):
        self.url = url
        self.on_receive = on_receive

        self.websocket = None
        self.message_task = None
        self.stopped = False

    def connect(self):
        self.message_task = threading.Thread(target=self._start_message_thread)
        self.message_task.start()

    def _start_message_thread(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._message())
        loop.close()

    async def send(self, chunk: bytearray):
        if self.websocket:
            await self.websocket.send(chunk)

    async def _message(self):
        try:
            ssl_context = ssl.SSLContext()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            util.print("connect to " + self.url)

            self.websocket = await websockets.connect(self.url, subprotocols=["binary"], ping_interval=None,
                                                      ssl=ssl_context)
            while True:
                if self.stopped:
                    break
                meg = await self.websocket.recv()
                meg = json.loads(meg)
                text = meg["text"]
                util.print(str(meg))
                if 'mode' not in meg:
                    continue
                if meg['mode'] == "2pass-offline":
                    await self.on_receive(text)
        except Exception as e:
            util.print("Exception:" + str(e))

    async def stop(self):
        self.stopped = True
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

        if self.message_task:
            self.message_task.do_run = False
            try:
                self.message_task.join()
            except Exception:
                pass
            self.message_task = None
