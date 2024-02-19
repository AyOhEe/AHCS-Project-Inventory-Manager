import tkinter as tk


from tkinter import messagebox
from typing import Tuple


from pinmanager import PinManager, EmployeeRecord


class CreatePinWindow(tk.Toplevel):
    def __init__(self, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug

        #self.resizable(False, False)   
        self.title("Create new employee entry:")
        self.title_label = tk.Label(self, text="Create new employee entry:")

        self.name_textvar = tk.StringVar(self, value="John Doe")
        self.name_entry = tk.Entry(self, textvariable=self.name_textvar)
        self.name_entry_label = tk.Label(self, text="Name: ")

        self.pin_textvar = tk.StringVar(self, value="7296345")
        pin_validation = self.register(self.validate_pin)
        self.pin_entry = tk.Entry(self, textvariable=self.pin_textvar, validate='all', validatecommand=(pin_validation, "%P"))
        self.pin_entry_label = tk.Label(self, text="New PIN:")

        self.admin_boolvar = tk.BooleanVar(self)
        self.admin_checkbox = tk.Checkbutton(self, variable=self.admin_boolvar)
        self.admin_checkbox_label = tk.Label(self, text="Has administrator privileges? ")

        self.submit_button = tk.Button(self, text="Create new PIN", command=self.try_create_pin)


        self.title_label.grid(column=0, row=0)

        self.name_entry_label.grid(column=0, row=2)
        self.name_entry.grid(column=3, row=2)

        self.pin_entry_label.grid(column=0, row=3)
        self.pin_entry.grid(column=3, row=3)

        self.admin_checkbox_label.grid(column=0, row=4)
        self.admin_checkbox.grid(column=3, row=4)

        self.submit_button.grid(column=2, row=6)

    def validate_pin(self, P):
        if (str.isdigit(P) or P == ""):
            # "" or "Hello world!" == "Hello world!"
            if int(P or "0") >= 0:
                return True
        return False
        
    def check_is_valid_attempt(self) -> Tuple[bool, str, str]:
        name = self.name_textvar.get()
        pin = self.pin_textvar.get()

        if name.strip() == "":
            return False, "Invalid Name", "Name cannot be empty"
        
        if pin.strip() == "":
            return False, "Invalid PIN", "PIN cannot be empty"
        
        if not str.isdigit(pin):
            return False, "Invalid PIN", "PIN must be a non-negative number"
        
        return True, "", ""
        
    def try_create_pin(self):
        #ensure that the new data is valid
        valid, title, reason = self.check_is_valid_attempt()
        if not valid:
            messagebox.showerror(title, reason)
            return
        
        name = self.name_textvar.get().strip()
        pin = self.pin_textvar.get().strip()
        admin = self.admin_boolvar.get()
        
        if not PinManager.add_new_employee(pin, EmployeeRecord("", name, admin)):
            messagebox.showerror("Failure", "Unable to create PIN. Is this PIN already in use?")
            return
    
        messagebox.showinfo("Success", f"Successfully created PIN entry for {name}")