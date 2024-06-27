import requests


def call_xiaoai(url: str, auth: str, entity_id: str, text: str) -> str:
    return _call_intelligent_speaker(url, auth, entity_id, text, True)


def play_text(url: str, auth: str, entity_id: str, text: str) -> str:
    return _call_intelligent_speaker(url, auth, entity_id, text, False)


def _call_intelligent_speaker(url: str, auth: str, entity_id: str, text: str, execute: bool) -> str:
    headers = {
        'Authorization': f'Bearer {auth}',
        'Content-Type': 'application/json'
    }
    data = {
        'entity_id': entity_id,
        'text': text,
        'execute': execute,
        'silent': False
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception:
        return None
