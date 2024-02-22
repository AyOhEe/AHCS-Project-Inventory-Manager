import json
import traceback


from functools import wraps
from typing import List, Any, Optional, Tuple


class _Config:
    def __init__(self, config_path: str="config.json"):
        try:
            with open(config_path, "r") as f:
                self.config_values = json.load(f)
                self.config_path = config_path

        except fnfe as FileNotFoundError:
            print(f"ConfigManager: Could not find {config_path}")
            raise fnfe

        except jde as json.JSONDecodeError:
            print(f"ConfigManager: {config_path} contains invalid JSON!")
            raise jde


    #returns the corresponding value for a set of keys in the configuration
    def get_config_value(self, *keys: List[str]) -> Tuple[bool, Optional[Any]]:
        def recursive_get(sub_dict, *args):
            if len(args) == 0:
                return False, None
            
            if len(args) == 1:
                if args[0] in sub_dict:
                    return True, sub_dict[args[0]]
                else:
                    return False, None

            return recursive_get(sub_dict[args[0]], *args[1:])
        
        success, result = recursive_get(self.config_values, *keys)
        if success and isinstance(result, dict):
            return False, None #dictionary values should not be returned
        
        return success, result

    #sets the value in the configuration for the set of keys
    #if the entry does not exist, it will be created, but only if 
    #the parent entries already exist.
    #returns the new value    
    def set_config_value(self, value: Any, *keys: List[str]) -> Any:
        def recursive_set(sub_dict, *args):
            if len(args) == 0:
                raise KeyError("Configuration entry does not exist for ", *keys)

            if len(args) == 1:
                sub_dict[args[0]] = value
            else:
                recursive_set(sub_dict[args[0]], *args[1:])

        recursive_set(self.config_values, *keys)
        return self.get_config_value(*keys)
        
    #saves the current configuration values to disk.
    #by default this saves to the same file that was opened upon initialisation,
    #but this can be changed by providing a file path as override_path
    def save_config(self, override_path: Optional[str] = None) -> None:
        path = self.config_path
        if override_path != None:
            path = override_path

        with open(path, "w") as f:
            json.dump(self.config_values, f, indent=4)

class ConfigManager:
    __instance = None

    #ensures that an instance of the config manager exists before running the wrapped function
    def check_exists(f):
        
        @wraps(f)
        def wrapper(*args, **kwargs):
            if ConfigManager.__instance == None:
                ConfigManager.initialise()

            return f(*args, **kwargs)

        return wrapper

    #creates the configuration instance. if the config file is at a specific path,
    #this MUST be called before the ConfigManager can be used.
    @staticmethod
    def initialise(config_path: str="config.json") -> None:
        ConfigManager.__instance = _Config(config_path)

    #returns the corresponding value for a set of keys in the configuration
    @staticmethod
    @check_exists
    def get_config_value(*keys: List[str]) -> Tuple[bool, Optional[Any]]:
        return ConfigManager.__instance.get_config_value(*keys)
        
    #sets the value in the configuration for the set of keys
    #if the entry does not exist, it will be created, but only if 
    #the parent entries already exist.
    #returns the new value    
    @staticmethod
    @check_exists
    def set_config_value(value: Any, *keys: List[str]) -> Any:
        return ConfigManager.__instance.set_config_value(value, *keys)
      
    #saves the current configuration values to disk.
    #by default this saves to the same file that was opened upon initialisation,
    #but this can be changed by providing a file path as override_path
    @staticmethod  
    @check_exists
    def save_config(override_path: Optional[str] = None) -> None:
        return ConfigManager.__instance.save_config(override_path)
