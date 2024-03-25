import unittest


from pinmanager import UserDetails


class TestUserDetails(unittest.TestCase):
    #tests the creation of user details objects
    def test_0_construction(self):
        user_data = [("Hash1", "John Doe", True), ("Hash2", "Jane Doe", False), ("Hash3", "Adam", True)]
        for data in user_data:
            record = UserDetails(*data)

            self.assertEqual(record.PIN_hash, data[0])
            self.assertEqual(record.name, data[1])
            self.assertEqual(record.has_admin, data[2])

    #tests the conversion of user details objects to dictionaries
    def test_1_dict_conversion(self):
        user_data = [("Hash1", "John Doe", True), ("Hash2", "Jane Doe", False), ("Hash3", "Adam", True)]
        records = [UserDetails(*data) for data in user_data]
        
        for data, record in zip(user_data, records):
            dictionary = {"PIN_hash" : data[0], "name" : data[1], "has_admin" : data[2]}

            self.assertEqual(dictionary, record.dict_serialise())

