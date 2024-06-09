import queue
from threading import Thread, Event
from tkinter import filedialog, messagebox

import customtkinter as ctk

from horde_api import MODEL_OPTIONS, queue_generation, make_payload, check_status, download_image, convert_to_png


class MultiLinePromptDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Generate a QR Code"):
        super().__init__(parent)
        self.title(title)
        self.geometry("750x750")

        self.url = ""
        self.text_input = ""
        self.selected_model_var = ctk.StringVar(value=next(iter(MODEL_OPTIONS)))
        self.image_label = None
        self.url_label = None
        self.text_area = None
        self.url_entry = None
        self.model = None
        self.loading_label = None
        self.ok_button = None
        self.result_queue = queue.Queue()
        self.stop_flag = Event()
        self.active = True

        self.create_widgets()

    def create_widgets(self) -> None:
        ctk.CTkLabel(self, text="Enter the URL:").pack(pady=5)
        self.url_entry = ctk.CTkEntry(self, width=350)
        self.url_entry.pack(pady=5, expand=True)

        ctk.CTkLabel(self, text="Enter your image prompt:").pack(pady=5)
        self.text_area = ctk.CTkTextbox(self, wrap='word')
        self.text_area.pack(expand=True, fill='both')

        ctk.CTkLabel(self, text="Select Model:").pack(pady=5)
        model_menu = ctk.CTkOptionMenu(self, variable=self.selected_model_var, values=list(MODEL_OPTIONS))
        model_menu.pack(pady=5)

        self.loading_label = ctk.CTkLabel(self, text="")
        self.loading_label.pack(pady=5)

        self.image_label = ctk.CTkLabel(self, text="Output Image URL")
        self.image_label.pack(pady=1, expand=True)

        self.url_label = ctk.CTkTextbox(self, wrap='word', state='disabled')
        self.url_label.pack(pady=1, expand=True)

        self.create_buttons()

    def create_buttons(self) -> None:
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=5)

        self.ok_button = ctk.CTkButton(button_frame, text="Generate", command=self.apply)
        self.ok_button.pack(side=ctk.LEFT, padx=5)

        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.cancel)
        cancel_button.pack(side=ctk.LEFT, padx=5)

    def apply(self) -> None:
        self.url = self.url_entry.get().strip()
        self.text_input = self.text_area.get("1.0", "end").strip()
        self.model = self.selected_model_var.get()

        self.loading_label.configure(text="Generating your QR code, this could take a minute...")

        self.ok_button.configure(state='disabled')

        self.stop_flag.clear()
        Thread(target=self.run_generation_task).start()

        self.check_queue()

    def run_generation_task(self) -> None:
        payload = make_payload(self.text_input, self.url, self.model)
        task_id = queue_generation(payload)
        img_url = check_status(task_id, self.stop_flag)
        if img_url:
            self.result_queue.put(img_url)

    def check_queue(self) -> None:
        if not self.active:
            return
        try:
            img_url = self.result_queue.get_nowait()
            self.task_complete(img_url)
        except queue.Empty:
            self.after(100, self.check_queue)

    def cancel(self) -> None:
        self.active = False
        self.stop_flag.set()
        self.destroy()

    def task_complete(self, img_url) -> None:
        self.loading_label.configure(text="Generation complete!")

        self.url_label.configure(state='normal')
        self.url_label.delete("1.0", "end")
        self.url_label.insert("end", img_url)
        self.url_label.configure(state='disabled')

        self.update_idletasks()

        self.ok_button.configure(state='normal')

        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            try:
                download_image(img_url, file_path)
                convert_to_png(file_path)
                messagebox.showinfo("Success", "Image downloaded and converted to PNG successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))


def main() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    root.withdraw()
    MultiLinePromptDialog(root)
    root.mainloop()


if __name__ == '__main__':
    main()
