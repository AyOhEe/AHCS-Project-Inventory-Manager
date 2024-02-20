import atexit
import unittest
import traceback
import json
import os


from pinmanager import PinManager


class TestPinManager(unittest.TestCase):
    def tearDown(self):
        if os.path.exists("test_temp_data/dummydata.json"):
            os.remove("test_temp_data/dummydata.json")

    def test_0_pinmanager_initialisation(self):
        try:
            PinManager.initialise("test_temp_data/dummydata.json")
        except Exception as ex:
            self.fail(f"PinManager.initialise failure!")

        #if that succeeded, the pin manager shouldn't save it's data on exit anymore.
        atexit.unregister(PinManager._PinManager__instance.on_exit)