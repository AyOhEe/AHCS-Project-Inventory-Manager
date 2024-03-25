import atexit
import unittest
import traceback
import json
import os


from pinmanager import PinManager, UserDetails
from pinmanager.pinmanager import HASH_FUNCTION


from unittest import mock


class TestPinManager(unittest.TestCase):
    DUMMY_DATA_PATH = "test_temp_data/dummydata.json"
    EXAMPLE_EMPLOYEES = user_data = [
        ("1234567", "John Doe", True), 
        ("7654321", "Jane Doe", False), 
        ("7801425", "Adam", True)
    ]

    def setUp(self):
        self.remove_data_file()
        with open(TestPinManager.DUMMY_DATA_PATH, "w") as f:
            json.dump({"users" : []}, f)

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

        self.assertTrue(len(PinManager.get_users()) == 1)


        #invalid json - should raise an execption (not a specific exception class)
        self.remove_data_file()
        with open(TestPinManager.DUMMY_DATA_PATH, "w") as f:
            f.write("this is not valid JSON")

        with self.assertRaises(Exception):
            PinManager.initialise(TestPinManager.DUMMY_DATA_PATH)
            atexit.unregister(PinManager._PinManager__instance.on_exit)


        #doesn't contain an users entry
        self.remove_data_file()
        with open(TestPinManager.DUMMY_DATA_PATH, "w") as f:
            json.dump(dict(), f)
        PinManager.initialise(TestPinManager.DUMMY_DATA_PATH)
        atexit.unregister(PinManager._PinManager__instance.on_exit)

        self.assertEqual(dict(), PinManager.get_users())


        #filled with records
        records = [UserDetails(HASH_FUNCTION(data[0]), data[1], data[2]) for data in TestPinManager.EXAMPLE_EMPLOYEES]
        filled_dict = {"users" : [
            record.dict_serialise() for record in records
        ]}
        expected_result = {record.PIN_hash : record for record in records}

        with open(TestPinManager.DUMMY_DATA_PATH, "w") as f:
            json.dump(filled_dict, f)
        PinManager.initialise(TestPinManager.DUMMY_DATA_PATH)
        atexit.unregister(PinManager._PinManager__instance.on_exit)

        self.assertEqual(PinManager.get_users(), expected_result)

    #tests the creation of user entries
    def test_1_pinmanager_add_user(self):
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            expected_hash = HASH_FUNCTION(data[0])
            record = UserDetails("", data[1], data[2])
            ret_val = PinManager.add_new_user(data[0], record)

            stored_record = PinManager.get_user(expected_hash)
            self.assertEqual(ret_val, stored_record)
            self.assertEqual(expected_hash, stored_record.PIN_hash)
            self.assertEqual(record.name, stored_record.name)
            self.assertEqual(record.has_admin, stored_record.has_admin)

            ret_val = PinManager.add_new_user(data[0], record)
            self.assertFalse(ret_val)

    def test_2_pinmanager_update_user(self):
        records = []
        new_records = []
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            record = UserDetails("", data[1], data[2])
            new_record = UserDetails("", data[1] + "_NEW", not data[2])
            records.append(PinManager.add_new_user(data[0], record))
            new_records.append(new_record)
        
        for record, new_record in zip(records, new_records):
            self.assertEqual(record, PinManager.get_user(record.PIN_hash))
            PinManager.update_user(record.PIN_hash, new_record)
            self.assertEqual(new_record, PinManager.get_user(record.PIN_hash))

        nonexistent_hashes = ["abcd", "1234", "5678", "efgh"]
        for hash in nonexistent_hashes:
            self.assertFalse(PinManager.update_user(hash, UserDetails("", "", "")))

    def test_3_pinmanager_remove_user(self):
        self.assertEqual(PinManager.get_users(), dict())

        records = []
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            record = UserDetails("", data[1], data[2])
            records.append(PinManager.add_new_user(data[0], record))
        
        for record in records:
            self.assertEqual(record, PinManager.get_user(record.PIN_hash))
            PinManager.remove_user(record.PIN_hash)
            self.assertFalse(PinManager.get_user(record.PIN_hash))

        nonexistent_hashes = ["abcd", "1234", "5678", "efgh"]
        for hash in nonexistent_hashes:
            self.assertFalse(PinManager.remove_user(hash))

    def test_4_pinmanager_get_user(self):
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            expected_hash = HASH_FUNCTION(data[0])
            self.assertFalse(PinManager.get_user(expected_hash))

            record = UserDetails("", data[1], data[2])
            PinManager.add_new_user(data[0], record)
            self.assertEqual(record, PinManager.get_user(expected_hash))

    def test_5_pinmanager_get_users(self):
        self.assertEqual(PinManager.get_users(), dict())

        records = []
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            record = UserDetails("", data[1], data[2])
            records.append(PinManager.add_new_user(data[0], record))

            expected_users = {record.PIN_hash : record for record in records}
            self.assertEqual(PinManager.get_users(), expected_users)

    def test_6_pinmanager_verify_pin(self):
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            self.assertFalse(PinManager.verify_pin(data[0], False))
            self.assertFalse(PinManager.verify_pin(data[0], True))

            record = UserDetails("", data[1], data[2])
            PinManager.add_new_user(data[0], record)

            self.assertTrue(PinManager.verify_pin(data[0], False))
            self.assertEqual(PinManager.verify_pin(data[0], True), data[2])

    def test_7_pinmanager_save_to_disk(self):
        self.assertEqual(dict(), PinManager.get_users())
        
        records = []
        for data in TestPinManager.EXAMPLE_EMPLOYEES:
            record = UserDetails("", data[1], data[2])
            records.append(PinManager.add_new_user(data[0], record))

        PinManager.save_to_disk()


        expected_data = {
            "users" : [record.dict_serialise() for record in records]
        }
        with open(TestPinManager.DUMMY_DATA_PATH, "r") as f:
            actual_data = json.load(f)
        self.assertEqual(expected_data, actual_data)

    def test_8_default_initialise(self):
        func_was_called = False
        original_initialise = PinManager.initialise
        def initialise_replacement():
            nonlocal func_was_called
            
            original_initialise(TestPinManager.DUMMY_DATA_PATH)
            atexit.unregister(PinManager._PinManager__instance.on_exit)
            func_was_called = True

        def verify_called():
            nonlocal func_was_called

            self.assertTrue(func_was_called)
            func_was_called = False
            PinManager._PinManager__instance = None

        #this test only ensures that each PinManager method initialises the interface
        #so it's completely fine to replace the method here
        with mock.patch.object(PinManager, 'initialise', initialise_replacement):
            PinManager.initialise()
            verify_called()

            PinManager.verify_pin("This doesn't exist and isn't meant to.")
            verify_called()

            PinManager.add_new_user("1234", UserDetails("", "Test name", False))
            verify_called()

            PinManager.update_user("Doesn't exist", UserDetails("", "Test name", False))
            verify_called()

            PinManager.remove_user("Doesn't exist")
            verify_called()

            PinManager.get_users()
            verify_called()

            PinManager.get_user("Doesn't exist")
            verify_called()

            PinManager.save_to_disk()
            verify_called()