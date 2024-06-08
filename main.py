import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
from threading import Thread, Event
import queue

from horde_api import MODEL_OPTIONS, queue_generation, make_payload, check_status, download_image, convert_to_png


class MultiLinePromptDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None) -> None:
        self.url = ""
        self.text_input = ""
        self.selected_model = tk.StringVar()
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
        super().__init__(parent, title=title)

    def body(self, master) -> tk.Entry:
        self.geometry("600x750")

        tk.Label(master, text="Enter the URL:").pack()
        self.url_entry = tk.Entry(master, width=100)
        self.url_entry.pack(pady=5)

        tk.Label(master, text="Enter your image prompt:").pack()
        self.text_area = tk.Text(master, wrap='word')
        self.text_area.pack(expand=True, fill='both')

        tk.Label(master, text="Select Model:").pack()
        self.selected_model.set(next(iter(MODEL_OPTIONS)))
        model_menu = tk.OptionMenu(master, self.selected_model, *MODEL_OPTIONS)
        model_menu.pack(pady=5)

        self.loading_label = tk.Label(master, text="", fg="black")
        self.loading_label.pack()

        self.image_label = tk.Label(master)
        self.image_label.pack(pady=10)

        self.url_label = tk.Text(master, height=5, wrap='word', bg="lightgrey", state='disabled')
        self.url_label.pack(pady=0)

        return self.url_entry

    def apply(self) -> None:
        self.url = self.url_entry.get().strip()
        self.text_input = self.text_area.get("1.0", tk.END).strip()
        self.model = self.selected_model.get()

        self.loading_label.config(text="Generating your QR code, this could take a minute...", fg="black")

        self.ok_button.config(state='disabled')

        self.stop_flag.clear()
        Thread(target=self.run_generation_task).start()

        self.check_queue()

    def run_generation_task(self) -> None:
        task_id = queue_generation(make_payload(self.text_input, self.url, self.model))
        img_url = check_status(task_id, self.stop_flag)
        if img_url:
            self.result_queue.put(img_url)

    def check_queue(self):
        if not self.active:
            return
        try:
            img_url = self.result_queue.get_nowait()
            self.task_complete(img_url)
        except queue.Empty:
            self.after(100, self.check_queue)

    def buttonbox(self) -> None:
        box = tk.Frame(self)

        self.ok_button = tk.Button(box, text="Generate", width=10, command=self.apply, default=tk.ACTIVE)
        self.ok_button.pack(side=tk.LEFT, padx=5, pady=5)

        cancel_button = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", lambda event: self.apply())
        self.bind("<Escape>", lambda event: self.cancel())

        box.pack()

    def cancel(self, event=None):
        self.active = False
        self.stop_flag.set()
        super().cancel(event)

    def task_complete(self, img_url) -> None:
        self.loading_label.config(text="Generation complete!", fg="green")

        self.url_label.config(state='normal')
        self.url_label.delete(1.0, tk.END)
        self.url_label.insert(tk.END, img_url)
        self.url_label.config(state='disabled')

        self.update_idletasks()

        self.ok_button.config(state='normal')

        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            try:
                download_image(img_url, file_path)
                convert_to_png(file_path)
                messagebox.showinfo("Success", "Image downloaded and converted to PNG successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    MultiLinePromptDialog(root, title="Generate a QR Code")
