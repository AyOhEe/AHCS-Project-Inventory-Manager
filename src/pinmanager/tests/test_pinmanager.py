import atexit
import unittest
import traceback
import json
import os


from pinmanager import PinManager, EmployeeRecord
from pinmanager.pinmanager import HASH_FUNCTION


class TestPinManager(unittest.TestCase):
    DUMMY_DATA_PATH = "test_temp_data/dummydata.json"
    EXAMPLE_EMPLOYEES = employee_data = [
        ("1234567", "John Doe", True), 
        ("7654321", "Jane Doe", False), 
        ("7801425", "Adam", True)
    ]

    def setUp(self):
        self.remove_data_file()
        with open(TestPinManager.DUMMY_DATA_PATH, "w") as f:
            json.dump({"employees" : []}, f)

    def tearDown(self):
        self.remove_data_file()

    def remove_data_file(self):
        if os.path.exists(TestPinManager.DUMMY_DATA_PATH):
            os.remove(TestPinManager.DUMMY_DATA_PATH)

    #tests the initialisation of the pin manager
    def test_0_pinmanager_initialisation(self):
        try:
            PinManager.initialise(TestPinManager.DUMMY_DATA_PATH)
        except Exception as ex:
            self.fail(f"PinManager.initialise failure!")

        #if that succeeded, the pin manager shouldn't save it's data on exit anymore.
        atexit.unregister(PinManager._PinManager__instance.on_exit)

    #tests the creation of employee entries
    def test_1_pinmanager_add_employee(self):
        PinManager.initialise(TestPinManager.DUMMY_DATA_PATH)
        atexit.unregister(PinManager._PinManager__instance.on_exit)

        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            expected_hash = HASH_FUNCTION(data[0])
            record = EmployeeRecord("", data[1], data[2])
            ret_val = PinManager.add_new_employee(data[0], record)

            stored_record = PinManager.get_employee(expected_hash)
            self.assertEqual(ret_val, stored_record)
            self.assertEqual(expected_hash, stored_record.PIN_hash)
            self.assertEqual(record.name, stored_record.name)
            self.assertEqual(record.has_admin, stored_record.has_admin)

            ret_val = PinManager.add_new_employee(data[0], record)
            self.assertFalse(ret_val)

    @unittest.expectedFailure
    def test_2_pinmanager_update_employee(self):
        self.fail("Unimplemented test.")

    def test_3_pinmanager_remove_employee(self):
        PinManager.initialise(TestPinManager.DUMMY_DATA_PATH)
        atexit.unregister(PinManager._PinManager__instance.on_exit)
        self.assertEqual(PinManager.get_employees(), dict())

        records = []
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            record = EmployeeRecord("", data[1], data[2])
            records.append(PinManager.add_new_employee(data[0], record))
        
        for record in records:
            self.assertEqual(record, PinManager.get_employee(record.PIN_hash))
            PinManager.get_employee(record.PIN_hash)
            self.assertFalse(PinManager.get_employee(record.PIN_hash))

    @unittest.expectedFailure
    def test_4_pinmanager_get_employee(self):
        self.fail("Unimplemented test.")

    def test_5_pinmanager_get_employees(self):
        PinManager.initialise(TestPinManager.DUMMY_DATA_PATH)
        atexit.unregister(PinManager._PinManager__instance.on_exit)
        self.assertEqual(PinManager.get_employees(), dict())

        records = []
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            record = EmployeeRecord("", data[1], data[2])
            records.append(PinManager.add_new_employee(data[0], record))

            expected_employees = {record.PIN_hash : record for record in records}
            self.assertEqual(PinManager.get_employees(), expected_employees)

    def test_6_pinmanager_verify_pin(self):
        PinManager.initialise(TestPinManager.DUMMY_DATA_PATH)
        atexit.unregister(PinManager._PinManager__instance.on_exit)

        records = []
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            self.assertFalse(PinManager.verify_pin(data[0], False))
            self.assertFalse(PinManager.verify_pin(data[0], True))

            record = EmployeeRecord("", data[1], data[2])
            records.append(PinManager.add_new_employee(data[0], record))

            self.assertTrue(PinManager.verify_pin(data[0], False))
            self.assertEqual(PinManager.verify_pin(data[0], True), data[2])

    def test_7_pinmanager_save_to_disk(self):
        PinManager.initialise(TestPinManager.DUMMY_DATA_PATH)
        atexit.unregister(PinManager._PinManager__instance.on_exit)
        self.assertEqual(dict(), PinManager.get_employees())
        
        
        records = []
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            record = EmployeeRecord("", data[1], data[2])
            records.append(PinManager.add_new_employee(data[0], record))

        PinManager.save_to_disk()


        expected_data = {
            "employees" : [record.dict_serialise() for record in records]
        }
        with open(TestPinManager.DUMMY_DATA_PATH, "r") as f:
            actual_data = json.load(f)
        self.assertEqual(expected_data, actual_data)
