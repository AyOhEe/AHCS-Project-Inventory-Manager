import tkinter as tk


from pinmanager import PinManager

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
        for i, e in enumerate(employees*10):
            table_widgets.append(self.create_table_entry(entries_table, e, i))

    def create_table_entry(self, table, employee, index):
        widgets = []

        widgets.append(tk.Label(table, text=employee.name))
        widgets.append(tk.Checkbutton(table, state=tk.DISABLED))
        if employee.has_admin:
            widgets[-1].select()
        widgets.append(tk.Button(table, text="Update Entry"))
        widgets.append(tk.Button(table, text="Remove Entry"))

        for i, w in enumerate(widgets):
            w.grid(row=index, column=i)

        return widgets