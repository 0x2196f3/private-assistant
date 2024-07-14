import datetime
import sys
from typing import Any

from eff_word_net.audio_processing import MODEL_TYPE_MAPPER


def log(text: Any):
    text = str(text)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sys.stdout.write(f"[{current_time}] {text}\n")
    sys.stdout.flush()


def create_model(model_name: str) -> object:
    if model_name in MODEL_TYPE_MAPPER:
        return MODEL_TYPE_MAPPER[model_name]()
    else:
        raise ValueError(f"Invalid model name: {model_name}")
