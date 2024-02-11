import tkinter as tk

class CreatePinWindow(tk.Toplevel):
    def __init__(self, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug