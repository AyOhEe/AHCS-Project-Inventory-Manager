import json
import hashlib
import atexit


from functools import wraps
from dataclasses import dataclass


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
    def __init__(self):
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

        with open("EmployeeData.json", "w") as f:
            json.dump(data, f, indent=4)

    #if the file exists, read the employee PIN hashes and records. otherwise returns empty list
    def read_records(self):
        #attempt to open the file containing the employee data (if it exists)
        try:
            f = open("EmployeeData.json", "r")

        except OSError:
            #whoops, doesn't exist, just create it return an empty list for now
            with open("EmployeeData.json", "w") as f:
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
    def verify_pin(self, pin, requires_admin):
        #hash the pin
        hash = HASH_FUNCTION(pin)

        #verify the pin exists
        valid = hash in self.employee_records
        #verify the pin has adequate authority
        authority = (self.employee_records[hash].has_admin) or (not requires_admin)

        #the pin is okay if it exists and has sufficient authority for this action
        return valid and authority



#class which all PIN requests and changes are directed to. hides an instance of the
#real pin manager using the singleton design pattern
class PinManager:
    #the instance of the _PinManagerInstance class
    __instance = _PinManagerInstance()


    #ensures that an instance of the pin manager exists before running the wrapped function
    def check_exists(f):

        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if PinManager.__instance == None:
                PinManager.__instance = _PinManagerInstance()

            return f(*args, **kwargs)

        return wrapper

    @classmethod
    @check_exists
    def verify_pin(pin, requires_admin):
        return PinManager.__instance.verify_pin(pin, requires_admin)
