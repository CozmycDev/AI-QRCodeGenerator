# horde_api.py
import random
import time
import requests

CLIENT_AGENT: str = "AI-QRCodeGenerator"
HORDE_URL: str = "https://aihorde.net/api"
HORDE_KEY: str = "0000000000"

IMAGE_MODEL: str = "AlbedoBase XL (SDXL)"
STEPS: int = 30
GUIDANCE_SCALE: float = 6.0
WIDTH: int = 1024
HEIGHT: int = 1024
CLIP_SKIP: int = 2
KARRAS: bool = False


def make_headers() -> dict:
    return {
        "Content-Type": "application/json",
        "Client-Agent": CLIENT_AGENT,
        "apikey": HORDE_KEY
    }


def make_request(url: str, payload: dict = None, headers: dict = None) -> dict:
    response = requests.get(url) if payload is None else requests.post(url, json=payload, headers=headers)
    return response.json()


def generate_seed() -> str:
    return str(random.randint(0, 999999999))


def is_finished(response: dict) -> bool:
    return response['finished'] == 1


def get_image(response: dict) -> str:
    return response['generations'][0]['img']


def queue_generation(payload: dict) -> str:
    resp_json = make_request(f'{HORDE_URL}/v2/generate/async', payload, make_headers())
    print(resp_json)
    return resp_json['id']


def check_status(task_id, stop_flag) -> str:
    while not stop_flag.is_set():
        status = make_request(f'{HORDE_URL}/v2/generate/check/{task_id}')
        print(status)
        if is_finished(status):
            break
        time.sleep(1)
    else:
        return None

    final_status = make_request(f'{HORDE_URL}/v2/generate/status/{task_id}')
    print(final_status)

    return get_image(final_status)


def make_payload(prompt: str, url: str) -> dict:
    return {
        "prompt": prompt,
        "params": {
            "sampler_name": "k_dpmpp_2m",
            "toggles": [1, 4],
            "cfg_scale": GUIDANCE_SCALE,
            "seed": generate_seed(),
            "height": HEIGHT,
            "width": WIDTH,
            "karras": KARRAS,
            "steps": STEPS,
            "n": 1,
            "clip_skip": CLIP_SKIP,
            "workflow": "qr_code",
            "extra_texts": [
                {"reference": "qr_code", "text": url}
            ]
        },
        "nsfw": True,
        "trusted_workers": False,
        "slow_workers": True,
        "censor_nsfw": False,
        "workers": [],
        "worker_blacklist": False,
        "models": [IMAGE_MODEL],
        "r2": True,
        "shared": True
    }
