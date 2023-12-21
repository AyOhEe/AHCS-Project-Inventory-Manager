import asyncio

import tkinter as tk

class Dashboard(tk.Tk):
    async def async_mainloop(self, update_delay=0.1):
        self.loop_exit_trigger = False
        self.protocol("WM_DELETE_WINDOW", self.stop_loop)

        while not self.loop_exit_trigger:
            self.update()
            await asyncio.sleep(update_delay)

    def stop_loop(self):
        self.loop_exit_trigger = True