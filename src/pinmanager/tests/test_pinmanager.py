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

        PinManager.initialise(TestPinManager.DUMMY_DATA_PATH)
        atexit.unregister(PinManager._PinManager__instance.on_exit)

    def tearDown(self):
        self.remove_data_file()

    def remove_data_file(self):
        if os.path.exists(TestPinManager.DUMMY_DATA_PATH):
            os.remove(TestPinManager.DUMMY_DATA_PATH)

    #tests the initialisation of the pin manager
    def test_0_pinmanager_initialisation(self):
        #initialisation with a valid json file containing no records is already tested
        # - if setUp ran without throwing, then it works.
        
        #nonexistent file - one default entry is added
        self.remove_data_file()
        PinManager.initialise(TestPinManager.DUMMY_DATA_PATH)
        atexit.unregister(PinManager._PinManager__instance.on_exit)

        self.assertTrue(len(PinManager.get_employees) == 1)


        #invalid json - should raise an execption (not a specific exception class)
        self.remove_data_file()
        with open(TestPinManager.DUMMY_DATA_PATH, "w") as f:
            f.write("this is not valid JSON")

        with self.assertRaises(Exception):
            PinManager.initialise(TestPinManager.DUMMY_DATA_PATH)
            atexit.unregister(PinManager._PinManager__instance.on_exit)


        #doesn't contain an employees entry
        self.remove_data_file()
        with open(TestPinManager.DUMMY_DATA_PATH, "w") as f:
            json.dump(dict(), f)
        PinManager.initialise(TestPinManager.DUMMY_DATA_PATH)
        atexit.unregister(PinManager._PinManager__instance.on_exit)

        self.assertEqual(dict(), PinManager.get_employees())


        #filled with records
        records = [EmployeeRecord(HASH_FUNCTION(data[0]), data[1], data[2]) for data in PinManager.EXAMPLE_EMPLOYEES]
        filled_dict = {"employees" : [
            record.dict_serialise() for record in records
        ]}
        expected_result = {record.PIN_hash : record for record in records}

        with open(TestPinManager.DUMMY_DATA_PATH, "w") as f:
            json.dump(filled_dict, f)
        PinManager.initialise(TestPinManager.DUMMY_DATA_PATH)
        atexit.unregister(PinManager._PinManager__instance.on_exit)

        self.assertEqual(PinManager.get_employees(), expected_result)

    #tests the creation of employee entries
    def test_1_pinmanager_add_employee(self):
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

    def test_2_pinmanager_update_employee(self):
        records = []
        new_records = []
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            record = EmployeeRecord("", data[1], data[2])
            new_record = EmployeeRecord("", data[1] + "_NEW", not data[2])
            records.append(PinManager.add_new_employee(data[0], record))
            new_records.append(new_record)
        
        for record, new_record in zip(records, new_records):
            self.assertEqual(record, PinManager.get_employee(record.PIN_hash))
            PinManager.update_employee(record.PIN_hash, new_record)
            self.assertEqual(new_record, PinManager.get_employee(record.PIN_hash))

        nonexistent_hashes = ["abcd", "1234", "5678", "efgh"]
        for hash in nonexistent_hashes:
            self.assertFalse(PinManager.update_employee(hash, EmployeeRecord("", "", "")))

    def test_3_pinmanager_remove_employee(self):
        self.assertEqual(PinManager.get_employees(), dict())

        records = []
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            record = EmployeeRecord("", data[1], data[2])
            records.append(PinManager.add_new_employee(data[0], record))
        
        for record in records:
            self.assertEqual(record, PinManager.get_employee(record.PIN_hash))
            PinManager.remove_employee(record.PIN_hash)
            self.assertFalse(PinManager.get_employee(record.PIN_hash))

        nonexistent_hashes = ["abcd", "1234", "5678", "efgh"]
        for hash in nonexistent_hashes:
            self.assertFalse(PinManager.remove_employee(hash))

    def test_4_pinmanager_get_employee(self):
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            expected_hash = HASH_FUNCTION(data[0])
            self.assertFalse(PinManager.get_employee(expected_hash))

            record = EmployeeRecord("", data[1], data[2])
            PinManager.add_new_employee(data[0], record)
            self.assertEqual(record, PinManager.get_employee(expected_hash))

    def test_5_pinmanager_get_employees(self):
        self.assertEqual(PinManager.get_employees(), dict())

        records = []
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            record = EmployeeRecord("", data[1], data[2])
            records.append(PinManager.add_new_employee(data[0], record))

            expected_employees = {record.PIN_hash : record for record in records}
            self.assertEqual(PinManager.get_employees(), expected_employees)

    def test_6_pinmanager_verify_pin(self):
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            self.assertFalse(PinManager.verify_pin(data[0], False))
            self.assertFalse(PinManager.verify_pin(data[0], True))

            record = EmployeeRecord("", data[1], data[2])
            PinManager.add_new_employee(data[0], record)

            self.assertTrue(PinManager.verify_pin(data[0], False))
            self.assertEqual(PinManager.verify_pin(data[0], True), data[2])

    def test_7_pinmanager_save_to_disk(self):
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
