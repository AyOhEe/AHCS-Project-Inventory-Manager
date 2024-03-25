import asyncio
import tkinter as tk


from .create_pin import CreatePinWindow
from .user_entries import UserEntriesWindow


class Dashboard(tk.Tk):
    def __init__(self, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug


        #self.resizable(False, False)   
        self.title("Inventory manager: Pin manager")
        self.title_label = tk.Label(self, text="Pin manager")

        self.create_entry_button = tk.Button(self, text="Create entry", command=self.make_create_pin_window)
        self.view_entries_button = tk.Button(self, text="View entries", command=self.make_user_entries_window)


        #place the widgets
        self.title_label.pack()
        self.create_entry_button.pack()
        self.view_entries_button.pack()

    def make_create_pin_window(self):
        self.create_pin_window = CreatePinWindow(self)
        self.create_pin_window.grab_set()

    def make_user_entries_window(self):
        self.user_entries_window = UserEntriesWindow(self)
        self.user_entries_window.grab_set()

    async def async_mainloop(self, update_delay=0.1):
        self.loop_exit_trigger = False
        self.protocol("WM_DELETE_WINDOW", self.stop_loop)

        while not self.loop_exit_trigger:
            self.update()
            await asyncio.sleep(update_delay)

    def stop_loop(self):
        self.loop_exit_trigger = True