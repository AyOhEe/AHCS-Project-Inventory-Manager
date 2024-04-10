import unittest
import json
import os
import configparser


from listingmanager import ListingManager, Listing
from listingmanager.listingmanager import _ListingManagerInstance


class TestListingManager(unittest.TestCase):
    DUMMY_MANIFEST_FILE = "test_temp_data/listing_manifest.json"
    DUMMY_CATEGORIES_FILE = "test_temp_data/listing_categories.txt"
    DUMMY_MANUFACTURERS_FILE = "test_temp_data/listing_manufacturers.txt"

    DUMMY_CATEGORIES = ["Category 1", "Category 2", "Category 3"]
    DUMMY_MANUFACTURERS = ["Manufacturer 1", "Manufacturer 2", "Manufacturer 3"]

    DUMMY_BAD_MANIFEST = {}
    DUMMY_BLANK_MANIFEST = {"listings" : []}
    DUMMY_VALID_MANIFEST = {"listings" : [_ListingManagerInstance.hash("Listing 1") + ".json", "doesn't exist", "bad_listing.json"]}

    DUMMY_LISTING_FILE = "test_temp_data/" + DUMMY_VALID_MANIFEST["listings"][0]
    DUMMY_BAD_LISTING_FILE = "test_temp_data/" + DUMMY_VALID_MANIFEST["listings"][2]
    DUMMY_LISTING = Listing("Listing 1", "Description 1", 0, 0, 0)

    DUMMY_CONFIG_FILE = "test_temp_data/config.json"
    DUMMY_CONFIG_DATA = dict()


    EXAMPLE_DATA = [
        ("Listing 1", "Description 1", 0, 1, 0),
        ("Listing 2", "Description 2", 1, 2, 123),
        ("Listing 3", "Description 3", 3, 0, 200),
        ("Alphabetically out of order", "Description 4", 0, 3, 0),
    ]


    def setUp(self):
        with open(TestListingManager.DUMMY_CONFIG_FILE, "w") as f:
            json.dump(TestListingManager.DUMMY_CONFIG_DATA, f)
        self.config_parser = configparser.ConfigParser()

        self.prepare_config()
        self.prepare_blank_manifest()
        ListingManager.initialise(self.config_parser)

    def tearDown(self):
        self.delete_all_listings() 
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

    def delete_all_listings(self):
        listings = ListingManager.get_all_listings()
        for listing in listings:
            ListingManager.remove_listing(ListingManager.get_listing_index(listing.name))

        
    def prepare_config(self):
        self.config_parser.add_section("Listings")
        self.config_parser["Listings"]["CategoriesPath"] = TestListingManager.DUMMY_CATEGORIES_FILE
        self.config_parser["Listings"]["ManufacturersPath"] = TestListingManager.DUMMY_MANUFACTURERS_FILE
        self.config_parser["Listings"]["ManifestPath"] = TestListingManager.DUMMY_MANIFEST_FILE

        with open(TestListingManager.DUMMY_CATEGORIES_FILE, "w") as f:
            f.writelines(TestListingManager.DUMMY_CATEGORIES)

        with open(TestListingManager.DUMMY_MANUFACTURERS_FILE, "w") as f:
            f.writelines(TestListingManager.DUMMY_MANUFACTURERS)


    def prepare_blank_manifest(self):
        with open(TestListingManager.DUMMY_MANIFEST_FILE, "w") as f:
            json.dump(TestListingManager.DUMMY_BLANK_MANIFEST, f)


    def test_0_initialise(self):
        self.assertEqual(ListingManager.get_all_listings(), [])


        self.remove_manifest()
        with self.assertRaises(FileNotFoundError):
            ListingManager.initialise(self.config_parser, TestListingManager.DUMMY_MANIFEST_FILE)

        with self.assertRaises(FileNotFoundError):
            ListingManager.initialise(self.config_parser)


        with open(TestListingManager.DUMMY_MANIFEST_FILE, "w") as f:
            json.dump(TestListingManager.DUMMY_BAD_MANIFEST, f)
        with self.assertRaises(ValueError):
            ListingManager.initialise(self.config_parser)

        with open(TestListingManager.DUMMY_MANIFEST_FILE, "w") as f:
            json.dump(TestListingManager.DUMMY_BLANK_MANIFEST, f)
        ListingManager.initialise(self.config_parser)


        with open(TestListingManager.DUMMY_MANIFEST_FILE, "w") as f:
            json.dump(TestListingManager.DUMMY_VALID_MANIFEST, f)
        with open(TestListingManager.DUMMY_LISTING_FILE, "w") as f:
            json.dump(TestListingManager.DUMMY_LISTING.as_dict(), f)
        with open(TestListingManager.DUMMY_BAD_LISTING_FILE, "w") as f:
            f.write("This isn't valid JSON.")
        ListingManager.initialise(self.config_parser)

    def test_1_create_listing(self):
        for data in TestListingManager.EXAMPLE_DATA:
            self.assertEqual(ListingManager.get_listing_index(data[0]), -1)
            self.assertTrue(ListingManager.create_listing(data[0], data[1], data[2], data[3])[0])
            self.assertNotEqual(ListingManager.get_listing_index(data[0]), -1)
            self.assertFalse(ListingManager.create_listing(data[0], data[1], data[2], data[3])[0])
            self.assertNotEqual(ListingManager.get_listing_index(data[0]), -1)

    def test_2_update_listing(self):
        for data in TestListingManager.EXAMPLE_DATA:
            ListingManager.create_listing(data[0], data[1], data[2], data[3])
            expected_listing = Listing(data[0], data[1], data[2], data[3], 0)
            self.assertEqual(ListingManager.get_listing(ListingManager.get_listing_index(data[0])), expected_listing)

            new_name = data[0] + " new"
            new_description = data[1] + " new"
            new_category = data[2] + 1
            new_manufacturer = data[3] + 1
            expected_listing = Listing(new_name, new_description, new_category, new_manufacturer, 0)
            ListingManager.update_listing(ListingManager.get_listing_index(data[0]), new_name, new_description, new_category, new_manufacturer)
            self.assertEqual(ListingManager.get_listing(ListingManager.get_listing_index(new_name)), expected_listing)
        
            ListingManager.remove_listing(ListingManager.get_listing_index(new_name))

    def test_3_remove_listing(self):
        for data in TestListingManager.EXAMPLE_DATA:
            ListingManager.create_listing(data[0], data[1], data[2], data[3])
            index = ListingManager.get_listing_index(data[0])
            self.assertNotEqual(index, -1)

            listing = ListingManager.remove_listing(index)
            self.assertEqual(Listing(data[0], data[1], data[2], data[3], 0), listing)

            filename = _ListingManagerInstance.hash(listing.name) + ".json"
            filepath = os.path.join(ListingManager._ListingManager__instance.directory, filename)
            self.assertFalse(os.path.exists(filepath))
        
    def test_4_get_listing_index(self):
        self.assertEqual(ListingManager.get_all_listings(), [])

        expected_index = 0
        for data in TestListingManager.EXAMPLE_DATA:
            ListingManager.create_listing(data[0], data[1], data[2], data[3])
            index = ListingManager.get_listing_index(data[0])
            self.assertEqual(expected_index, index)
            expected_index += 1
        
    def test_5_add_stock(self):
        for data in TestListingManager.EXAMPLE_DATA:
            ListingManager.create_listing(data[0], data[1], data[2], data[3])
            index = ListingManager.get_listing_index(data[0])
            expected_quantity = 0

            expected_quantity += 10
            ListingManager.add_stock(index, 10)
            self.assertEqual(expected_quantity, ListingManager.get_listing(index).quantity)
        
    def test_6_remove_stock(self):
        for data in TestListingManager.EXAMPLE_DATA:
            ListingManager.create_listing(data[0], data[1], data[2], data[3])
            index = ListingManager.get_listing_index(data[0])
            expected_quantity = 0

            expected_quantity += 10
            self.assertTrue(ListingManager.add_stock(index, 10))
            self.assertEqual(expected_quantity, ListingManager.get_listing(index).quantity)

            self.assertFalse(ListingManager.remove_stock(index, 11))
            self.assertEqual(expected_quantity, ListingManager.get_listing(index).quantity)

            self.assertTrue(ListingManager.remove_stock(index, 10))
            expected_quantity -= 10
            self.assertEqual(expected_quantity, ListingManager.get_listing(index).quantity)
        

    def test_7_get_all_listings(self):
        listings = []
        for data in TestListingManager.EXAMPLE_DATA:
            ListingManager.create_listing(data[0], data[1], data[2], data[3])
            expected_listing = Listing(data[0], data[1], data[2], data[3], 0)
            self.assertEqual(ListingManager.get_listing(ListingManager.get_listing_index(data[0])), expected_listing)
            listings.append(expected_listing)

        self.assertEqual(listings, ListingManager.get_all_listings())
        
    def test_8_get_listing(self):
        for data in TestListingManager.EXAMPLE_DATA:
            expected_listing = Listing(data[0], data[1], data[2], data[3], 0)
            self.assertEqual(ListingManager.get_listing_index(expected_listing.name), -1)

            ListingManager.create_listing(data[0], data[1], data[2], data[3])
            index = ListingManager.get_listing_index(data[0])
            self.assertNotEqual(index, -1)

            self.assertEqual(ListingManager.get_listing(index), expected_listing)
        
    def test_9_query_listings(self):
        listings = []
        for data in TestListingManager.EXAMPLE_DATA:
            ListingManager.create_listing(data[0], data[1], data[2], data[3])
            expected_listing = Listing(data[0], data[1], data[2], data[3], 0)
            listings.append(expected_listing)

        expected_results = [
            sorted(listings, key=lambda x: x.name),
            [listings[0], listings[1], listings[2]],
            [listings[3]],
            [listings[3], listings[0]],
            [listings[0]]
        ]
        arguments = [
            ("", -1, -1),
            ("Listing", -1, -1),
            ("Alphabetically", -1, -1),
            ("", 0, -1),
            ("", 0, 1)
        ]

        for args, expected_result in zip(arguments, expected_results):
            self.assertEqual(expected_result, ListingManager.query_listings(*args))


    #TODO test that categories and manufacturers are being correctly parsed
    #NOTE actually no don't do that, just talk about it instead