import unittest
import json
import os


from configmanager import ConfigManager


from unittest import mock


class TestConfigManager(unittest.TestCase):
    DUMMY_CONFIG_PATH = "dummyconfig.json"
    DUMMY_DATA = {
        "not nested" : 1,
        "nested" : {
            "value" : 2,
            "double nested": {
                "value" : 3
            }
        }
    }

    def setUp(self):
        self.remove_dummy_config()
        with open(TestConfigManager.DUMMY_CONFIG_PATH, "w") as f:
            json.dump(TestConfigManager.DUMMY_DATA, f)

        ConfigManager.initialise(TestConfigManager.DUMMY_CONFIG_PATH)

    def tearDown(self):
        self.remove_dummy_config()

    def remove_dummy_config(self):
        if os.path.exists(TestConfigManager.DUMMY_CONFIG_PATH):
            os.remove(TestConfigManager.DUMMY_CONFIG_PATH)

    def test_0_initialise(self):
        self.remove_dummy_config()
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

    def test_1_get_config_value(self):
        self.assertEqual(ConfigManager.get_config_value("not nested")[1], TestConfigManager.DUMMY_DATA["not nested"])
        self.assertEqual(ConfigManager.get_config_value("nested", "value")[1], TestConfigManager.DUMMY_DATA["nested"]["value"])
        self.assertEqual(ConfigManager.get_config_value("nested", "double nested", "value")[1], TestConfigManager.DUMMY_DATA["nested"]["double nested"]["value"])

        self.assertFalse(ConfigManager.get_config_value("nested")[0])
        self.assertFalse(ConfigManager.get_config_value("This Value Doesn't Exist")[0])
        self.assertFalse(ConfigManager.get_config_value()[0])

    def test_2_set_config_value(self):
        ConfigManager.set_config_value(56544574, "not nested")
        self.assertEqual(56544574, ConfigManager.get_config_value("not nested")[1])

        ConfigManager.set_config_value(124351, "nested", "value")
        self.assertEqual(124351, ConfigManager.get_config_value("nested", "value")[1])
        
        ConfigManager.set_config_value(6566586, "nested", "double nested", "value")
        self.assertEqual(6566586, ConfigManager.get_config_value("nested", "double nested", "value")[1])

        ConfigManager.set_config_value(12345, "new value")
        self.assertEqual(12345, ConfigManager.get_config_value("new value")[1])
        
        ConfigManager.set_config_value({"nested" : True}, "dictionary value")
        self.assertFalse(ConfigManager.get_config_value("dictionary value")[0])
        self.assertEqual(ConfigManager.get_config_value("dictionary value", "nested")[1], True)

        with self.assertRaises(KeyError):
            ConfigManager.set_config_value("This should throw, no keys were provided")
        
    def test_3_save_config(self):
        self.remove_dummy_config()

        ConfigManager.save_config()
        with open(TestConfigManager.DUMMY_CONFIG_PATH, "r") as f:
            self.assertEqual(TestConfigManager.DUMMY_DATA, json.load(f))

        override_path = TestConfigManager.DUMMY_CONFIG_PATH[:-5] + "_different path.json"
        ConfigManager.save_config(override_path)
        with open(override_path, "r") as f:
            self.assertEqual(TestConfigManager.DUMMY_DATA, json.load(f))

        os.remove(override_path)

    def test_4_default_initialise(self):
        func_was_called = False
        original_initialise = ConfigManager.initialise
        def initialise_replacement():
            nonlocal func_was_called
            
            original_initialise(TestConfigManager.DUMMY_CONFIG_PATH)
            func_was_called = True

        def verify_called():
            nonlocal func_was_called

            self.assertTrue(func_was_called)
            func_was_called = False
            ConfigManager._ConfigManager__instance = None

        #create the dummy config just so the config manager has something to work with
        with open(TestConfigManager.DUMMY_CONFIG_PATH, "w") as f:
            json.dump(dict(), f)

        #this test only ensures that each ConfigManager method initialises the interface
        #so it's completely fine to replace the method here
        with mock.patch.object(ConfigManager, 'initialise', initialise_replacement):
            ConfigManager.initialise()
            verify_called()

            ConfigManager.get_config_value()
            verify_called()

            with self.assertRaises(KeyError):
                ConfigManager.set_config_value(None)
            verify_called()

            ConfigManager.save_config()
            verify_called()

        self.remove_dummy_config()
        