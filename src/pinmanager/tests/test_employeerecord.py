import unittest


from pinmanager import EmployeeRecord


class TestEmployeeRecord(unittest.TestCase):
    #tests the creation of employee records
    def test_0_construction(self):
        employee_data = [("Hash1", "John Doe", True), ("Hash2", "Jane Doe", False), ("Hash3", "Adam", True)]
        for data in employee_data:
            record = EmployeeRecord(*data)

            self.assertEqual(record.PIN_hash, data[0])
            self.assertEqual(record.name, data[1])
            self.assertEqual(record.has_admin, data[2])

    #tests the conversion of employee records to dictionaries
    def test_1_dict_conversion(self):
        employee_data = [("Hash1", "John Doe", True), ("Hash2", "Jane Doe", False), ("Hash3", "Adam", True)]
        records = [EmployeeRecord(*data) for data in employee_data]
        
        for data, record in zip(employee_data, records):
            dictionary = {"PIN_hash" : data[0], "name" : data[1], "has_admin" : data[2]}

            self.assertEqual(dictionary, record.dict_serialise())

