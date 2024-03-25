import tkinter as tk


from tkinter import messagebox
from typing import Tuple


from pinmanager import PinManager, UserDetails

class UpdateEntryWindow(tk.Toplevel):
    def __init__(self, user, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug


        self.original_data = user

        #self.resizable(False, False)   
        self.title("Update user entry:")
        self.title_label = tk.Label(self, text="Update user entry:")

        self.name_textvar = tk.StringVar(self, value=user.name)
        self.name_entry = tk.Entry(self, textvariable=self.name_textvar)
        self.name_entry_label = tk.Label(self, text="Name: ")

        self.admin_boolvar = tk.BooleanVar(self, value=user.has_admin)
        self.admin_checkbox = tk.Checkbutton(self, variable=self.admin_boolvar)
        self.admin_checkbox_label = tk.Label(self, text="Has administrator privileges? ")

        self.submit_button = tk.Button(self, text="Update Entry", command=self.try_update_entry)


        self.title_label.grid(column=0, row=0)

        self.name_entry_label.grid(column=0, row=2)
        self.name_entry.grid(column=3, row=2)

        self.admin_checkbox_label.grid(column=0, row=3)
        self.admin_checkbox.grid(column=3, row=3)

        self.submit_button.grid(column=2, row=5)

    def validate_pin(self, P):
        if (str.isdigit(P) or P == ""):
            # "" or "Hello world!" == "Hello world!"
            if int(P or "0") >= 0:
                return True
        return False
    
    def check_is_valid_attempt(self) -> Tuple[bool, str, str]:
        name = self.name_textvar.get()

        if name.strip() == "":
            return False, "Invalid Name", "Name cannot be empty"
        
        return True, "", ""
        
    def try_update_entry(self):
        #ensure that the new data is valid
        valid, title, reason = self.check_is_valid_attempt()
        if not valid:
            messagebox.showerror(title, reason)
            return
        
        name = self.name_textvar.get().strip()
        has_admin = self.admin_boolvar.get()

        new_user = UserDetails(self.original_data.PIN_hash, name, has_admin)
        PinManager.update_user(self.original_data.PIN_hash, new_user)
    
        messagebox.showinfo("Success", f"Successfully updated PIN entry for {name}")