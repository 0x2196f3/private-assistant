import asyncio
import json
import shutil
import time

import const
import home_assistant
import util
from MainThreadLooper import MainThreadLooper
from eff_word_net.engine import HotwordDetector
from eff_word_net.streams import SimpleMicStream
from FunASR import FunASR
from Listener import Listener
import numpy as np

shutil.copyfile("/config/config.py", "/app/config.py")
import config


def on_receive(text: str) -> None:
    home_assistant.call_xiaoai(config.xiaoai_url, config.ha_auth, config.entity_id, text)
    looper.send(asr.stop, None, None)


asr = FunASR(config.asr_url, on_receive=on_receive)


def on_detect(mic_stream: SimpleMicStream) -> None:
    asr.start()

    home_assistant.play_text(config.xiaoai_url, config.ha_auth, config.entity_id, "我在")

    mic_stream._out_audio = np.zeros(mic_stream._window_size)

    mic_stream.mic_stream.read(int(const.samplerate * 2.5))

    message = json.dumps({"mode": "2pass", "chunk_size": [5, 10, 5], "chunk_interval": 10,
                          "wav_name": "microphone", "is_speaking": True, "hotwords": config.hotwords, "itn": True})

    asr.send(message)

    chuck_size = const.chuck_size

    for _ in range(int(const.samplerate * 10 / chuck_size)):
        data = mic_stream.mic_stream.read(chuck_size)
        if data is None:
            break
        if asr.is_stopped():
            break
        try:
            asr.send(data)
        except Exception as e:
            print(e)
        time.sleep(0.005)


hw = HotwordDetector(
    hotword=config.hotword_path[config.hotword_path.rindex("/") + 1:],
    reference_file=config.hotword_path,
    model=util.create_model(config.model),
    threshold=config.threshold,
    relaxation_time=5
)

mic_stream = SimpleMicStream()

listener = Listener(hw, mic_stream, on_detect)
listener.start()

looper = MainThreadLooper()
looper.run()
