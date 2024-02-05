import json
import traceback


from functools import wraps


class _Config:
    def __init__(self, config_path="config.json"):
        try:
            with open(config_path, "r") as f:
                self.config_values = json.load(f)
                self.config_path = config_path

        except FileNotFoundError:
            print(f"ConfigManager: Could not find {config_path}")

        except json.JSONDecodeError:
            print(f"ConfigManager: {config_path} contains invalid JSON!")
            traceback.print_exc()

    def get_config_value(self, *keys):
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

        
    def set_config_value(self, value, *keys):
        def recursive_set(sub_dict, *args):
            if len(args) == 0:
                return

            if len(args) == 1:
                sub_dict[args[0]] = value
            else:
                recursive_set(sub_dict[args[0]], *args[1:])

        recursive_set(self.config_values, *keys)
        return self.get_config_value(*keys)
        
    def save_config(self, override_path = None):
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

    @staticmethod
    def initialise(config_path="config.json"):
        ConfigManager.__instance = _Config(config_path)

    @staticmethod
    @check_exists
    def get_config_value(*keys):
        return ConfigManager.__instance.get_config_value(*keys)
        
    @staticmethod
    @check_exists
    def set_config_value(keys, value):
        return ConfigManager.__instance.set_config_value(keys, value)
      
    @staticmethod  
    @check_exists
    def save_config(override_path = None):
        return ConfigManager.__instance.save_config(override_path)

if __name__ == "__main__":
    ConfigManager.initialise("config.json")


    print(test_val := ConfigManager.get_config_value("test")[1])
    print(ConfigManager.get_config_value("a", "b", "c"))
    print(ConfigManager.set_config_value(test_val + 1, "test"))
    print(ConfigManager.get_config_value("test"))
    ConfigManager.save_config()

