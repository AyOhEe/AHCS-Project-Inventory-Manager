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
class UserDetails:
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
    def on_exit(self): #pragma: no cover
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

        except FileNotFoundError:
            #whoops, doesn't exist, just create it return an empty list for now
            with open(self.employee_data_file, "w") as f:
                f.write(DEFAULT_EMPLOYEE_DATA_JSON)
            hash = HASH_FUNCTION(DEFAULT_ADMIN_PIN)
            return {hash : UserDetails(hash, "Default Administrator PIN", True)}
        
        #variables initialised within a try-except block do not get deleted when that block ends
        #attempt to load the json file as a dictionary
        try:
            data = json.loads(f.read())
        except json.JSONDecodeError:
            #file no longer in use - close it
            f.close()

            #whoa. that's kinda bad. the json file contained bad JSON.
            #assuming that the program never wrote bad JSON, someone tampered with it
            #or there's been a hardware failure. #TODO adequate response for this scenario
            raise Exception("Employee data file couldn't be read properly. Have you edited it manually? You may have hardware issues.")

        #okay, we read the file successfully. now we create the employee records from it
        if "employees" not in data:
            #file no longer in use - close it
            f.close()

            #TODO this should probably complain a lot more
            #no data
            return {}
        
        #create the list of records from all valid entries
        records_dict = {}
        for employee in data["employees"]:
            if ("PIN_hash" in employee) and ("name" in employee) and ("has_admin" in employee):
                records_dict[employee["PIN_hash"]] = \
                    UserDetails(employee["PIN_hash"], employee["name"], employee["has_admin"])


        #file no longer in use - close it
        f.close()

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
    def add_new_employee(self, pin: str, employee: UserDetails) -> bool | UserDetails:
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
    def update_employee(self, hash: str, new_record: UserDetails) -> bool | UserDetails:
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
    def remove_employee(self, hash: str) -> bool | UserDetails:
        if hash in self.employee_records:
            #return the old record for convenience. can be ignored if it's not useful
            return self.employee_records.pop(hash)
        
        #employee wasn't there, return False to indicate failure
        return False
    
    #returns a copy dictionary (i.e. the user can't modify it) of the employee records
    def get_employees(self) -> typing.Dict[str, UserDetails]:
        return dict(self.employee_records)
    
    def get_employee(self, hash: str) -> bool | UserDetails:
        if hash in self.employee_records:
            return copy.deepcopy(self.employee_records[hash])
        
        return False
        



#TODO rename everything to USER instead of EMPLOYEE
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
    def initialise(data_path=None):
        PinManager.__instance = _PinManagerInstance(data_path)

    @staticmethod
    @check_exists
    def verify_pin(pin, requires_admin: bool = False) -> bool:
        return PinManager.__instance.verify_pin(pin, requires_admin)
    
    @staticmethod
    @check_exists
    def add_new_employee(pin: str, employee: UserDetails) -> bool | UserDetails:
        ret = PinManager.__instance.add_new_employee(pin, employee)
        PinManager.__instance.save_to_disk()
        return ret
    
    @staticmethod
    @check_exists
    def update_employee(hash: str, new_record: UserDetails) -> bool | UserDetails:
        ret = PinManager.__instance.update_employee(hash, new_record)
        PinManager.__instance.save_to_disk()
        return ret
    
    @staticmethod
    @check_exists
    def remove_employee(hash: str) -> bool | UserDetails:
        ret = PinManager.__instance.remove_employee(hash)
        PinManager.__instance.save_to_disk()
        return ret
    
    @staticmethod
    @check_exists
    def get_employees() -> typing.Dict[str, UserDetails]:
        return PinManager.__instance.get_employees()
    
    @staticmethod
    @check_exists
    def get_employee(hash) -> bool | UserDetails:
        return PinManager.__instance.get_employee(hash)
    
    @staticmethod
    @check_exists
    def save_to_disk() -> None:
        return PinManager.__instance.save_to_disk()
