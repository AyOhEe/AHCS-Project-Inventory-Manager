import unittest
import json
import os


from listingmanager import ListingManager, Listing
from configmanager import ConfigManager


class TestListingManager(unittest.TestCase):
    DUMMY_MANIFEST_FILE = "test_temp_data/listing_manifest.json"
    DUMMY_CATEGORIES_FILE = "test_temp_data/listing_categories.txt"
    DUMMY_MANUFACTURERS_FILE = "test_temp_data/listing_manufacturers.txt"

    DUMMY_CATEGORIES = ["Category 1", "Category 2", "Category 3"]
    DUMMY_MANUFACTURERS = ["Manufacturer 1", "Manufacturer 2", "Manufacturer 3"]

    DUMMY_BAD_MANIFEST = {}
    DUMMY_BLANK_MANIFEST = {"listings" : []}
    DUMMY_VALID_MANIFEST = {"listings" : ["dummy_listing.json", "doesn't exist", "bad_listing.json"]}

    DUMMY_LISTING_FILE = "test_temp_data/dummy_listing.json"
    DUMMY_BAD_LISTING_FILE = "test_temp_data/bad_listing.json"
    DUMMY_LISTING = Listing("Listing 1", "Description 1", 0, 0, 0)

    DUMMY_CONFIG_FILE = "test_temp_data/config.json"
    DUMMY_CONFIG_DATA = dict()

    def setUp(self):
        with open(TestListingManager.DUMMY_CONFIG_FILE, "w") as f:
            json.dump(TestListingManager.DUMMY_CONFIG_DATA, f)
        ConfigManager.initialise(TestListingManager.DUMMY_CONFIG_FILE)

    def tearDown(self):
        self.remove_manifest()
        self.remove_listing_files()
        self.remove_config_files()

    def remove_manifest(self):
        if os.path.exists(TestListingManager.DUMMY_MANIFEST_FILE):
            os.remove(TestListingManager.DUMMY_MANIFEST_FILE)

    def remove_listing_files(self):
        if os.path.exists(TestListingManager.DUMMY_LISTING_FILE):
            os.remove(TestListingManager.DUMMY_LISTING_FILE)
        
        if os.path.exists(TestListingManager.DUMMY_BAD_LISTING_FILE):
            os.remove(TestListingManager.DUMMY_BAD_LISTING_FILE)

    def remove_config_files(self):
        if os.path.exists(TestListingManager.DUMMY_CATEGORIES_FILE):
            os.remove(TestListingManager.DUMMY_CATEGORIES_FILE)

        if os.path.exists(TestListingManager.DUMMY_MANUFACTURERS_FILE):
            os.remove(TestListingManager.DUMMY_MANUFACTURERS_FILE)

        if os.path.exists(TestListingManager.DUMMY_CONFIG_FILE):
            os.remove(TestListingManager.DUMMY_CONFIG_FILE)
        
    def prepare_config(self):
        with open(TestListingManager.DUMMY_CATEGORIES_FILE, "w") as f:
            for category in TestListingManager.DUMMY_CATEGORIES:
                f.write(category + "\n")

        with open(TestListingManager.DUMMY_MANUFACTURERS_FILE, "w") as f:
            for manufacturer in TestListingManager.DUMMY_MANUFACTURERS:
                f.write(manufacturer + "\n")

        ConfigManager.set_config_value(TestListingManager.DUMMY_CATEGORIES_FILE, "listing categories file")
        ConfigManager.set_config_value(TestListingManager.DUMMY_MANUFACTURERS_FILE, "listing manufacturers file")
        ConfigManager.set_config_value(TestListingManager.DUMMY_MANIFEST_FILE, "listings manifest")

    def test_0_initialise(self):
        #TODO ensure this covers all cases.
        self.remove_manifest()
        self.prepare_config()
        with self.assertRaises(FileNotFoundError):
            ListingManager.initialise(TestListingManager.DUMMY_MANIFEST_FILE)

        with self.assertRaises(FileNotFoundError):
            ListingManager.initialise()


        with open(TestListingManager.DUMMY_MANIFEST_FILE, "w") as f:
            json.dump(TestListingManager.DUMMY_BAD_MANIFEST, f)
        with self.assertRaises(ValueError):
            ListingManager.initialise()

        with open(TestListingManager.DUMMY_MANIFEST_FILE, "w") as f:
            json.dump(TestListingManager.DUMMY_BLANK_MANIFEST, f)
        ListingManager.initialise()


        with open(TestListingManager.DUMMY_MANIFEST_FILE, "w") as f:
            json.dump(TestListingManager.DUMMY_VALID_MANIFEST, f)
        with open(TestListingManager.DUMMY_LISTING_FILE, "w") as f:
            json.dump(TestListingManager.DUMMY_LISTING.as_dict(), f)
        with open(TestListingManager.DUMMY_BAD_LISTING_FILE, "w") as f:
            f.write("This isn't valid JSON.")
        ListingManager.initialise()

    @unittest.expectedFailure
    def test_1_create_listing(self):
        self.fail("Unimplemented test")
        
    @unittest.expectedFailure
    def test_2_update_listing(self):
        self.fail("Unimplemented test")
        
    @unittest.expectedFailure
    def test_3_remove_listing(self):
        self.fail("Unimplemented test")
        
    @unittest.expectedFailure
    def test_4_get_listing_index(self):
        self.fail("Unimplemented test")
        
    @unittest.expectedFailure
    def test_5_add_stock(self):
        self.fail("Unimplemented test")
        
    @unittest.expectedFailure
    def test_6_remove_stock(self):
        self.fail("Unimplemented test")
        

    @unittest.expectedFailure
    def test_7_get_all_listings(self):
        self.fail("Unimplemented test")
        
    @unittest.expectedFailure
    def test_8_get_listing(self):
        self.fail("Unimplemented test")
        
    @unittest.expectedFailure
    def test_9_query_listings(self):
        self.fail("Unimplemented test")
        