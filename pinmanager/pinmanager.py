

from functools import wraps


#class which all PIN requests and changes are directed to. hides an instance of the
#real pin manager using the singleton design pattern
class PinManager:
    #the instance of the _PinManagerInstance class
    __instance = None


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
    
#the class which actually handles PIN management. only one instance of this should ever exist,
#managed by PinManager
class _PinManagerInstance:

    def verify_pin(self, pin, requires_admin):
        return True