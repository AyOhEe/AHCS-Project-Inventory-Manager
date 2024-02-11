import tkinter as tk

class UpdateEntryWindow(tk.Toplevel):
    def __init__(self, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug