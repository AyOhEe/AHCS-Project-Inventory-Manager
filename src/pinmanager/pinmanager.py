import json
import hashlib
import atexit
import copy
import typing


from functools import wraps
from dataclasses import dataclass


from configmanager import ConfigManager


#NOTE don't move this to a config file - this should all be hardcoded and NOT accessible to the user
#having a constant reference to this means it is trivial to replace it in the future
HASH_FUNCTION = lambda x: hashlib.sha512(x.encode('utf-8'), usedforsecurity=True).hexdigest()
DEFAULT_ADMIN_PIN = "3685368"
DEFAULT_EMPLOYEE_DATA_JSON = f"""{{
    "employees" : [
        {{
            "PIN_hash" : "{HASH_FUNCTION(DEFAULT_ADMIN_PIN)}",
            "name" : "Default Administrator PIN",
            "has_admin" : true
        }}
    ]
}}
"""


    
@dataclass
class EmployeeRecord:
    PIN_hash: str = ""
    name: str = ""
    has_admin: bool = False

    #returns a representation of this object as a dictionary. used for data storage
    def dict_serialise(self):
        return {"PIN_hash" : self.PIN_hash, "name" : self.name, "has_admin" : self.has_admin}

#the class which actually handles PIN management. only one instance of this should ever exist,
#managed by PinManager
class _PinManagerInstance:
    def __init__(self, datapath=None):
        self.employee_data_file = datapath or ConfigManager.get_config_value("employee data path")[1]
        self.employee_records = self.read_records()

        atexit.register(self.on_exit)

    #save the PIN hashes to disk when the program exits
    def on_exit(self):
        self.save_to_disk()
    
    #saves all employee data to disk
    def save_to_disk(self):
        data = { "employees" : []}

        for hash, record in self.employee_records.items():
            data["employees"].append(record.dict_serialise())

        with open(self.employee_data_file, "w") as f:
            json.dump(data, f, indent=4)

    #if the file exists, read the employee PIN hashes and records. otherwise returns empty list
    def read_records(self):
        #attempt to open the file containing the employee data (if it exists)
        try:
            f = open(self.employee_data_file, "r")

        except OSError:
            #whoops, doesn't exist, just create it return an empty list for now
            with open(self.employee_data_file, "w") as f:
                f.write(DEFAULT_EMPLOYEE_DATA_JSON)
            hash = HASH_FUNCTION(DEFAULT_ADMIN_PIN)
            return {hash : EmployeeRecord(hash, "Default Administrator PIN", True)}
        
        #variables initialised within a try-except block do not get deleted when that block ends
        #attempt to load the json file as a dictionary
        try:
            data = json.loads(f.read())
        except json.JSONDecodeError:
            #whoa. that's kinda bad. the json file contained bad JSON.
            #assuming that the program never wrote bad JSON, someone tampered with it
            #or there's been a hardware failure. #TODO adequate response for this scenario
            raise Exception("Employee data file couldn't be read properly. Have you edited it manually? You may have hardware issues.")

        #okay, we read the file successfully. now we create the employee records from it
        if "employees" not in data:
            #TODO this should probably complain a lot more
            #no data
            return {}
        
        #create the list of records from all valid entries
        records_dict = {}
        for employee in data["employees"]:
            if ("PIN_hash" in employee) and ("name" in employee) and ("has_admin" in employee):
                records_dict[employee["PIN_hash"]] = \
                    EmployeeRecord(employee["PIN_hash"], employee["name"], employee["has_admin"])

        return records_dict


    #returns true if the hash of this pin exists in the employee records
    def verify_pin(self, pin: str, requires_admin: bool) -> bool:
        #hash the pin
        hash = HASH_FUNCTION(pin)

        #verify the pin exists
        valid = hash in self.employee_records
        #verify the pin has adequate authority
        if valid:
            authority = (self.employee_records[hash].has_admin) or (not requires_admin)
        else:
            return False

        #the pin is okay if it exists and has sufficient authority for this action
        return valid and authority
    
    #adds a new employee record to the pin manager with the given pin.
    #returns the new employee record on success, otherwise returns False
    def add_new_employee(self, pin: str, employee: EmployeeRecord) -> bool | EmployeeRecord:
        #generate the hash for their PIN
        hash = HASH_FUNCTION(pin)

        #ensure that someone does not already share this PIN
        if hash in self.employee_records:
            return False

        #store the employee and their hash
        self.employee_records[hash] = employee
        self.employee_records[hash].PIN_hash = hash
        #return the new record for convenience. can be ignored if it's not useful
        return self.employee_records[hash]
    
    #takes an employee hash and replaces their employee record with the supplied one
    #returns False on failure and the new record on success
    def update_employee(self, hash: str, new_record: EmployeeRecord) -> bool | EmployeeRecord:
        #simply do the replacement, authorisation should be managed elsewhere
        if hash in self.employee_records:
            self.employee_records[hash] = new_record
            #hash might not be supplied in the new record, so set it just in case
            self.employee_records[hash].PIN_hash = hash 
            #return the new record for convenience. can be ignored if it's not useful
            return self.employee_records
        
        #employee wasn't there, return False to indicate failure
        return False
        
    #removes an employee from the records
    #returns false on failure, the old record on success
    def remove_employee(self, hash: str) -> bool | EmployeeRecord:
        if hash in self.employee_records:
            #return the old record for convenience. can be ignored if it's not useful
            return self.employee_records.pop(hash)
        
        #employee wasn't there, return False to indicate failure
        return False
    
    #returns a copy dictionary (i.e. the user can't modify it) of the employee records
    def get_employees(self) -> typing.Dict[str, EmployeeRecord]:
        return dict(self.employee_records)
    
    def get_employee(self, hash: str) -> bool | EmployeeRecord:
        if hash in self.employee_records:
            return copy.deepcopy(self.employee_records[hash])
        
        return False
        



#class which all PIN requests and changes are directed to. hides an instance of the
#real pin manager using the singleton design pattern
class PinManager:
    #the instance of the _PinManagerInstance class
    __instance: _PinManagerInstance = None


    #ensures that an instance of the pin manager exists before running the wrapped function
    #NOTE: this absorbs the reference of "self" given to functions. this class shouldn't ever
    #      have instance methods anyway, so that isn't an issue, but keep this in mind if adding
    #      functions to this class
    def check_exists(f):

        @wraps(f)
        def wrapper(*args, **kwargs):
            if PinManager.__instance == None:
                PinManager.initialise()

            return f(*args, **kwargs)

        return wrapper

    @staticmethod
    def initialise(datapath=None):
        PinManager.__instance = _PinManagerInstance(datapath)

    @staticmethod
    @check_exists
    def verify_pin(pin, requires_admin: bool = False) -> bool:
        return PinManager.__instance.verify_pin(pin, requires_admin)
    
    @staticmethod
    @check_exists
    def add_new_employee(pin: str, employee: EmployeeRecord) -> bool | EmployeeRecord:
        ret = PinManager.__instance.add_new_employee(pin, employee)
        PinManager.__instance.save_to_disk()
        return ret
    
    @staticmethod
    @check_exists
    def update_employee(hash: str, new_record: EmployeeRecord) -> bool | EmployeeRecord:
        ret = PinManager.__instance.update_employee(hash, new_record)
        PinManager.__instance.save_to_disk()
        return ret
    
    @staticmethod
    @check_exists
    def remove_employee(hash: str) -> bool | EmployeeRecord:
        ret = PinManager.__instance.remove_employee(hash)
        PinManager.__instance.save_to_disk()
        return ret
    
    @staticmethod
    @check_exists
    def get_employees() -> typing.Dict[str, EmployeeRecord]:
        return PinManager.__instance.get_employees()
    
    @staticmethod
    @check_exists
    def get_employee(hash) -> EmployeeRecord:
        return PinManager.__instance.get_employee(hash)


if __name__ == "__main__":
    import os


    #reset the employee data and restart the pin manager
    os.remove("EmployeeData.json")
    PinManager.initialise()

    #add a new key and check that it exists
    PinManager.add_new_employee("1234567", EmployeeRecord("", "John Doe", False))
    if PinManager.verify_pin("1234567"):
        print("Pin successfully added")
    else:
        print("Pin unsuccessfully added")
        quit()


    #get a record of all employee hashes and take the first one
    hashes = [k for k in PinManager.get_employees().keys()]
    hash = hashes[0]

    #attempt to update it and verify that the change went through
    record = EmployeeRecord("", "Jane Doe", True)
    PinManager.update_employee(hash, record)

    if (new_record := PinManager.get_employee(hash)):
        if new_record == record:
            print("Employee update success")
        else:
            print("Employee update failure")


    #remove the employee then verify that it was removed
    if not PinManager.remove_employee(hash):
        print("Employee not in record (??? this shouldn't happen ???)")
        quit()
    
    if PinManager.get_employee(hash):
        print("Employee was found after deletion. Failure.")
        quit()
    else:
        print("Employee successfully removed!")

    #this enables the following ansi escape for console colours. don't ask me why
    #we need to do this, it's just how it is AFAIK
    os.system("") 
    print("\n\n\t\t\033[0;32mFull basic test pass!\033[37m")

