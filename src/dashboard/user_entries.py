import tkinter as tk


from tkinter import messagebox


from pinmanager import PinManager
from .update_entry import UpdateEntryWindow

class UserEntriesWindow(tk.Toplevel):
    def __init__(self, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug

        self.title("Inventory manager: User entries")
        self.title_label = tk.Label(self, text="User entries:")

        self.entries_table = tk.Frame(self)
        self.create_table_entries(self.entries_table)

        self.title_label.grid(row=0, column=0, sticky=tk.W)
        self.entries_table.grid(row=2, column=0)   

    def create_table_entries(self, entries_table):
        users = [v for v in PinManager.get_users().values()]
        table_widgets = []
        for i, e in enumerate(users):
            table_widgets.append(self.create_table_entry(entries_table, e, i))

    def create_table_entry(self, table, user, index):
        widgets = []

        widgets.append(tk.Label(table, text=user.name))
        widgets.append(tk.Checkbutton(table, state=tk.DISABLED))
        if user.has_admin:
            widgets[-1].select()
        widgets.append(tk.Button(table, text="Update Entry", command=self.make_update_entry_window(user)))
        widgets.append(tk.Button(table, text="Remove Entry", command=self.remove_entry(user)))

        for i, w in enumerate(widgets):
            w.grid(row=index, column=i)

        return widgets
    

    def make_update_entry_window(self, user):
        return lambda: self._make_update_entry_window(user)
    
    def _make_update_entry_window(self, user):
        self.update_entry_window = UpdateEntryWindow(user, self)
        self.update_entry_window.grab_set()

    
    def remove_entry(self, user):
        return lambda: self._remove_entry(user)

    def _remove_entry(self, user):
        if messagebox.askyesno("Remove Entry", f"Are you sure you would like to remove {user.name}?"):
            if PinManager.remove_user(user.PIN_hash):
                messagebox.showinfo("Success", f"Successfully removed {user.name}")
            else:
                messagebox.showerror("Failure", "Failed to remove entry. This is most likely a bug, please restart the program and try again.")

        #TODO refresh page