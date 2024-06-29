import asyncio
import queue
import sys
import threading

from eff_word_net.audio_processing import MODEL_TYPE_MAPPER


def print(text: str):
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def create_model(model_name: str) -> object:
    if model_name in MODEL_TYPE_MAPPER:
        return MODEL_TYPE_MAPPER[model_name]()
    else:
        raise ValueError(f"Invalid model name: {model_name}")