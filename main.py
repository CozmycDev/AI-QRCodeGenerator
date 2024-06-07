import random
import tkinter as tk
from tkinter import simpledialog

import requests
import time


class HordeAPI:
    def __init__(self, dialog=None):
        self.horde_url = "https://aihorde.net/api"
        self.dialog = dialog

    def queue_generation(self, payload):
        headers = {
            "Content-Type": "application/json",
            "Client-Agent": "AI-QRCodeGenerator",
            "apikey": "0000000000"
        }

        resp = requests.post(f'{self.horde_url}/v2/generate/async', json=payload, headers=headers)
        resp_json = resp.json()
        print(resp_json)

        self.dialog.update_idletasks()

        return resp_json['id']

    def check_status(self, task_id):
        while True:
            self.dialog.update_idletasks()

            status_resp = requests.get(f'{self.horde_url}/v2/generate/check/{task_id}')
            status = status_resp.json()
            print(status)

            if status['finished'] == 1:
                break

            time.sleep(1)

        final_status_resp = requests.get(f'{self.horde_url}/v2/generate/status/{task_id}')
        final_status = final_status_resp.json()
        print(final_status)

        self.dialog.update_idletasks()

        return final_status['generations'][0]['img']


class MultiLinePromptDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None):
        self.url = ""
        self.text_input = ""
        self.negative_input = ""
        self.image_label = None
        self.url_label = None
        super().__init__(parent, title=title)

    def body(self, master):
        self.geometry("600x650")

        tk.Label(master, text="Enter the URL:").pack()
        self.url_entry = tk.Entry(master, width=100)
        self.url_entry.pack(pady=5)

        tk.Label(master, text="Enter your image prompt:").pack()
        self.text_area = tk.Text(master, wrap='word')
        self.text_area.pack(expand=True, fill='both')

        self.loading_label = tk.Label(master, text="", fg="red")
        self.loading_label.pack()

        self.image_label = tk.Label(master)
        self.image_label.pack(pady=10)

        self.url_label = tk.Text(master, height=5, wrap='word', bg="lightgrey", state='disabled')
        self.url_label.pack(pady=0)

        return self.url_entry

    def apply(self):
        self.url = self.url_entry.get().strip()
        self.text_input = self.text_area.get("1.0", tk.END).strip()

        self.loading_label.config(text="Generating your QR code, this could take a minute...")

        self.update_idletasks()

        self.ok_button.config(state='disabled')

        api = HordeAPI(self)

        task_id = api.queue_generation({
            "prompt": self.text_input,
            "params": {
                "sampler_name": "k_dpmpp_2m",
                "toggles": [1, 4],
                "cfg_scale": 6.0,
                "seed": str(random.randint(0, 999999999)),
                "height": 1024,
                "width": 1024,
                "karras": False,
                "steps": 30,
                "n": 1,
                "clip_skip": 2,
                "workflow": "qr_code",
                "extra_texts": [
                    {"reference": "qr_code", "text": self.url}
                ]
            },
            "nsfw": True,
            "trusted_workers": False,
            "slow_workers": True,
            "censor_nsfw": False,
            "workers": [],
            "worker_blacklist": False,
            "models": ['AlbedoBase XL (SDXL)'],
            "r2": True,
            "shared": True,
            "replacement_filter": True,
            "dry_run": False
        })

        img_url = api.check_status(task_id)

        self.task_complete(img_url)

    def buttonbox(self):
        box = tk.Frame(self)

        self.ok_button = tk.Button(box, text="OK", width=10, command=self.apply, default=tk.ACTIVE)
        self.ok_button.pack(side=tk.LEFT, padx=5, pady=5)

        cancel_button = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", lambda event: self.apply())
        self.bind("<Escape>", lambda event: self.cancel())

        box.pack()

    def task_complete(self, img_url):
        self.loading_label.config(text="Generation complete!", fg="red")

        self.url_label.config(state='normal')
        self.url_label.delete(1.0, tk.END)
        self.url_label.insert(tk.END, img_url)
        self.url_label.config(state='disabled')

        self.update_idletasks()

        self.ok_button.config(state='normal')


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    dialog = MultiLinePromptDialog(root, title="Generate a QR Code")
