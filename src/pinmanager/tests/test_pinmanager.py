import atexit
import unittest
import traceback
import json
import os


from pinmanager import PinManager


class TestPinManager(unittest.TestCase):
    def setUp(self):
        dummydata = {
            "employees": [
                {
                    "PIN_hash": "d40da9e902a33e5fbe7908fc10f9ce144b66b05c994f43ea488779b19a528bfc05f29e6b8f9947ad306fc4a31bf0f0bfd192f6c4d8578c9158142c433a517ebe",
                    "name": "Default Administrator PIN",
                    "has_admin": True
                }
            ]
        }

        with open("test_temp_data/dummydata.json", "w") as f:
            json.dump(dummydata, f)

    def tearDown(self):
        os.remove("test_temp_data/dummydata.json")

    def test_0_pinmanager_initialisation(self):
        try:
            PinManager.initialise("test_temp_data/dummydata.json")
        except Exception as ex:
            self.fail(f"PinManager.initialise failure!")

        #if that succeeded, the pin manager shouldn't save it's data on exit anymore.
        atexit.unregister(PinManager._PinManager__instance.on_exit)