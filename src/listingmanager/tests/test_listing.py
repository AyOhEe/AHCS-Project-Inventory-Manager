import unittest
import os
import json

from listingmanager import Listing


class TestListing(unittest.TestCase):
    DUMMY_CATEGORIES_FILE = "test_temp_data/categories.txt"
    DUMMY_MANUFACTURERS_FILE = "test_temp_data/manufacturers.txt"
    DUMMY_LISTING_FILE = "test_temp_data/listing.json"

    EXAMPLE_CATEGORIES = ["Category 1", "", "Category 2", "Category 1", "Category 3"]
    EXAMPLE_MANUFACTURERS = ["Manufacturer 1", "", "Manufacturer 2", "Manufacturer 1", "Manufacturer 3"]
    EXPECTED_CATEGORIES = ["Category 1", "Category 2", "Category 3"]
    EXPECTED_MANUFACTURERS = ["Manufacturer 1", "Manufacturer 2", "Manufacturer 3"]

    EXAMPLE_DATA = [
        ("Listing 1", "Description 1", 0, 1, 0),
        ("Listing 2", "Description 2", 1, 2, 123),
        ("Listing 3", "Description 3", 3, 0, 200),
    ]

    CONSTRUCTOR_EXAMPLE_DATA = [
        (False, "Listing 1", "Description 1", 0, 1, 0),
        (False, "Listing 2", "Description 2", 1, 2, 123),
        (True, "Listing 3", "Description 3", 2, 3, -200),
        (False, "Listing 4", "", 3, 0, 200),
        (True, "", "Description 5", 3, 0, 200),
        (True, "Listing 6", "Description 6", -1, 0, 0),
        (True, "Listing 7", "Description 7", 0, -1, 0)
    ]

    def tearDown(self):
        self.remove_listing_file()
        self.remove_categories()
        self.remove_manufacturers()

    def remove_listing_file(self):
        if os.path.exists(TestListing.DUMMY_LISTING_FILE):
            os.remove(TestListing.DUMMY_LISTING_FILE)

    def remove_categories(self):
        if os.path.exists(TestListing.DUMMY_CATEGORIES_FILE):
            os.remove(TestListing.DUMMY_CATEGORIES_FILE)

    def remove_manufacturers(self):
        if os.path.exists(TestListing.DUMMY_MANUFACTURERS_FILE):
            os.remove(TestListing.DUMMY_MANUFACTURERS_FILE)


    def prepare_categories(self):
        with open(TestListing.DUMMY_CATEGORIES_FILE, "w") as f:
            for category in TestListing.EXAMPLE_CATEGORIES:
                f.write(category + "\n")
        Listing.parse_categories(TestListing.DUMMY_CATEGORIES_FILE)
    
    def prepare_manufacturers(self):
        with open(TestListing.DUMMY_MANUFACTURERS_FILE, "w") as f:
            for manufacturer in TestListing.EXAMPLE_MANUFACTURERS:
                f.write(manufacturer + "\n")
        Listing.parse_manufacturers(TestListing.DUMMY_MANUFACTURERS_FILE)


    def test_0_parse_categories(self):
        self.remove_categories()
        Listing.parse_categories(TestListing.DUMMY_CATEGORIES_FILE)

        default_categories = {0 : "Unsorted"}
        self.assertEqual(default_categories, Listing.categories)


        self.prepare_categories()

        expected_result = default_categories | {i + 1 : l for i, l in enumerate(TestListing.EXPECTED_CATEGORIES)}
        self.assertEqual(expected_result, Listing.categories)
        self.remove_categories()
        Listing.categories = default_categories

    def test_1_parse_manufacturers(self):
        self.remove_manufacturers()
        Listing.parse_manufacturers(TestListing.DUMMY_MANUFACTURERS_FILE)
        
        default_manufacturers = {0 : "Manufacturer not listed"}
        self.assertEqual(default_manufacturers, Listing.manufacturers)


        self.prepare_manufacturers()

        expected_result = default_manufacturers | {i + 1 : l for i, l in enumerate(TestListing.EXPECTED_MANUFACTURERS)}
        self.assertEqual(expected_result, Listing.manufacturers)
        self.remove_manufacturers()
        Listing.manufacturers = default_manufacturers

    def test_2_from_file(self):
        self.prepare_manufacturers()
        self.prepare_categories()
        
        filenames = []
        listings = []
        should_fail = []
        i = 0
        for fails, *data in TestListing.CONSTRUCTOR_EXAMPLE_DATA:
            file = str(i) + ".json"
            i += 1
            filenames.append(file)

            listing = Listing(*data, _force_construct = True)
            listings.append(listing)
            should_fail.append(fails)

            with open(file, "w") as f:
                json.dump(listing.as_dict(), f)

        for file, listing, fails in zip(filenames, listings, should_fail):
            f = open(file, "r")
            if fails:
                with self.assertRaises(ValueError):
                    Listing.from_file(f)
            else:
                fromfile = Listing.from_file(f)[0]
                self.assertEqual(fromfile, listing)
            f.close()
            os.remove(file)

        

    def test_3_str(self):
        self.prepare_manufacturers()
        self.prepare_categories()

        for data in TestListing.EXAMPLE_DATA:
            fails = (not isinstance(data[2], int)) or (not isinstance(data[3], int)) \
                or (data[2] < 0) or (data[3] < 0)
            if fails:
                continue

            listing = Listing(*data)

            expected_str = "Listing: " + str(listing.quantity) + "*\"" \
                + Listing.manufacturers[listing.manufacturer] + " :: " \
                + str(listing.name) + "\" - " + Listing.categories[listing.category]\
                + "\n         " + listing.description[:30]
            self.assertEqual(expected_str, str(listing))

    def test_4_as_dict(self):
        for data in TestListing.EXAMPLE_DATA:
            listing = Listing(*data)

            expected_dict = {
                "name" : listing.name,
                "description" : listing.description,
                "category" : listing.category,
                "manufacturer" : listing.manufacturer,
                "quantity" : listing.quantity
            }
            self.assertEqual(expected_dict, listing.as_dict())

    def test_5_constructor(self):
        for fails, *data in TestListing.CONSTRUCTOR_EXAMPLE_DATA:
            if fails:
                #is meant to fail
                with self.assertRaises(ValueError):
                    listing = Listing(*data)
                continue

            #is meant to succeed
            listing = Listing(*data)

            self.assertEqual(listing.name, data[0])
            self.assertEqual(listing.description, data[1])
            self.assertEqual(listing.category, data[2])
            self.assertEqual(listing.manufacturer, data[3])
            self.assertEqual(listing.quantity, data[4])
        
    def test_6_eq(self):
        listings = []
        for data in TestListing.EXAMPLE_DATA:
            listing = Listing(*data)
            listings.append(listing)

        for i in range(1, len(listings)):
            self.assertNotEqual(listings[i], 0)
            self.assertNotEqual(listings[i], listings[i - 1])
            self.assertEqual(listings[i], listings[i])