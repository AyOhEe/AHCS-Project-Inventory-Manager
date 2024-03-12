import tkinter as tk


from tkinter import messagebox


from pinmanager import PinManager
from .update_entry import UpdateEntryWindow

class EmployeeEntriesWindow(tk.Toplevel):
    def __init__(self, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug

        self.title("Inventory manager: Employee entries")
        self.title_label = tk.Label(self, text="Employee entries:")

        self.entries_table = tk.Frame(self)
        self.create_table_entries(self.entries_table)

        self.title_label.grid(row=0, column=0, sticky=tk.W)
        self.entries_table.grid(row=2, column=0)   

    def create_table_entries(self, entries_table):
        employees = [v for v in PinManager.get_employees().values()]
        table_widgets = []
        for i, e in enumerate(employees):
            table_widgets.append(self.create_table_entry(entries_table, e, i))

    def create_table_entry(self, table, employee, index):
        widgets = []

        widgets.append(tk.Label(table, text=employee.name))
        widgets.append(tk.Checkbutton(table, state=tk.DISABLED))
        if employee.has_admin:
            widgets[-1].select()
        widgets.append(tk.Button(table, text="Update Entry", command=self.make_update_entry_window))
        widgets.append(tk.Button(table, text="Remove Entry", command=self.remove_entry(employee)))

        for i, w in enumerate(widgets):
            w.grid(row=index, column=i)

        return widgets
    
    def make_update_entry_window(self):
        self.update_entry_window = UpdateEntryWindow(self)
        self.update_entry_window.grab_set()


    def remove_entry(self, employee):
        return lambda: self._remove_entry(employee)

    def _remove_entry(self, employee):
        if messagebox.askyesno("Remove Entry", f"Are you sure you would like to remove {employee.name}?"):
            if PinManager.remove_employee(employee.PIN_hash):
                messagebox.showinfo("Success", f"Successfully removed {employee.name}")
            else:
                messagebox.showerror("Failure", "Failed to remove entry. This is most likely a bug, please restart the program and try again.")

        #TODO refresh page