import random
import time
import requests
from PIL import Image

CLIENT_AGENT: str = "AI-QRCodeGenerator"
HORDE_URL: str = "https://aihorde.net/api"
HORDE_KEY: str = "0000000000"

MODEL_OPTIONS: set = {
    'SDXL 1.0', 'AlbedoBase XL (SDXL)', 'Fustercluck', 'ICBINP XL', 'DreamShaper XL', 'Juggernaut XL',
}

STEPS: int = 30
SAMPLER: str = "k_euler"
GUIDANCE_SCALE: float = 5.5
WIDTH: int = 1024
HEIGHT: int = 1024
CLIP_SKIP: int = 2
KARRAS: bool = True


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


def make_payload(prompt: str, url: str, model: str) -> dict:
    return {
        "prompt": prompt,
        "params": {
            "sampler_name": SAMPLER,
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
        "models": [model],
        "r2": True,
        "shared": True
    }


def download_image(img_url: str, file_path: str) -> None:
    response = requests.get(img_url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(f"Failed to download image. Status code: {response.status_code}")


def convert_to_png(file_path: str) -> None:
    img = Image.open(file_path)
    png_path = file_path.rsplit('.', 1)[0] + '.png'
    img.save(png_path, format='PNG')
