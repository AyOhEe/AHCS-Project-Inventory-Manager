import unittest
import json
import os


from configmanager import ConfigManager


class TestConfigManager(unittest.TestCase):
    DUMMY_CONFIG_PATH = "dummyconfig.json"

    def test_0_initialise(self):
        os.remove(TestConfigManager.DUMMY_CONFIG_PATH)
        with self.assertRaises(FileNotFoundError):
            ConfigManager.initialise(TestConfigManager.DUMMY_CONFIG_PATH)
        

        with open(TestConfigManager.DUMMY_CONFIG_PATH, "w") as f:
            f.write("This is not valid JSON")
        with self.assertRaises(json.JSONDecodeError):
            ConfigManager.initialise(TestConfigManager.DUMMY_CONFIG_PATH)
        

        config_data = {"a" : 1, "b" : 2, "c" : 3}
        with open(TestConfigManager.DUMMY_CONFIG_PATH, "w") as f:
            json.dump(config_data, f)
        ConfigManager.initialise(TestConfigManager.DUMMY_CONFIG_PATH)

    @unittest.expectedFailure
    def test_1_get_config_value(self):
        self.fail("Unimplemented test")
        
    @unittest.expectedFailure
    def test_2_set_config_value(self):
        self.fail("Unimplemented test")
        
    @unittest.expectedFailure
    def test_3_save_config(self):
        self.fail("Unimplemented test")
        