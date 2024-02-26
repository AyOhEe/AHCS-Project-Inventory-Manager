import json
import traceback
import pathlib
import hashlib
import os


from functools import wraps


from . import Listing
from configmanager import ConfigManager


class _ListingManagerInstance:
    def __init__(self, listings_manifest = "listings/manifest.json"):
        #attempt to read the manifest
        with open(listings_manifest, "r") as f:
            manifest = json.load(f)
        
        #ensure that the manifest is valid
        if not "listings" in manifest:
            print(f"ListingManager: \"{listings_manifest}\" does not contain a \"listings\" entry!")
            raise ValueError(f"\"{listings_manifest}\" does not contain a \"listings\" entry!")

        #attempt to parse each listing
        self.parse_listings(manifest, listings_manifest)

    @staticmethod
    def hash(data):
        return hashlib.md5(data.encode("utf-8")).hexdigest()

    def parse_listings(self, manifest, manifest_path):
        self.listings = []
        self.directory = pathlib.Path(os.getcwd()).joinpath(pathlib.Path(manifest_path))
        self.directory = pathlib.Path(os.path.join(*self.directory.parts[:-1]))
        for file_name in manifest["listings"]:
            try:
                with open(os.path.join(self.directory, file_name), "r") as f:
                    listing, success = Listing.from_file(f)
                    if success:
                        self.listings.append(listing)

            except FileNotFoundError:
                print(f"ListingManager: Error opening file \"{file_name}\" found in manifest. Skipping...")
            
            except json.JSONDecodeError as jde:
                print(f"ListingManager: Error parsing file \"{file_name}\" found in manifest. Skipping...")
        

    def save_listings(self):
        #prepare the listings manifest and save each listing as we go
        listing_filenames = self.save_manifest()["listings"]

        for l in self.listings:
            #store the filename so it can be retrieved later
            name_hash = _ListingManagerInstance.hash(l.name)
            filename = f"{name_hash}.json"

            #open and save to each file
            path = os.path.join(self.directory, filename)
            try:
                with open(path, "w") as f:
                    json.dump(l.as_dict(), f)
            except FileNotFoundError:
                #TODO log error
                print("Could not open listing file {path}")


        

    def save_manifest(self):
        listings_manifest = {"listings" : []}
        for l in self.listings:
            name_hash = _ListingManagerInstance.hash(l.name)
            filename = f"{name_hash}.json"
            listings_manifest["listings"].append(filename)

        try:
            with open(ConfigManager.get_config_value("listings manifest")[1], "w") as f:
                json.dump(listings_manifest, f)
        except FileNotFoundError:
            #TODO log error
            print("Could not open listings manifest to save. This should not occur.")

        return listings_manifest

    def create_listing(self, name, desc, category, manufacturer):
        #enforce uniqueness
        if self.get_listing_index(name) != -1:
            return False, f"Name must be unique. \"{name}\" was already listed."

        self.listings.append(Listing(name, desc, category, manufacturer, 0))
        self.save_listings()
        return True, None

    def update_listing(self, index, new_name, new_description, new_category, new_manufacturer):
        self.listings[index].name = new_name
        self.listings[index].description = new_description
        self.listings[index].category = new_category
        self.listings[index].manufacturer = new_manufacturer

        self.save_listings()

    def remove_listing(self, listing_index):
        l = self.listings.pop(listing_index)
        self.save_manifest()

        filename = _ListingManagerInstance.hash(l.name) + ".json"
        os.remove(os.path.join(self.directory, filename))
        return l

    def get_listing_index(self, name):
        for i, l in enumerate(self.listings):
            if l.name == name:
                return i
            
        return -1


    def add_stock(self, listing_index, quantity):
        if self.listings[listing_index].quantity + quantity < 0:
            return False
        else:
            self.listings[listing_index].quantity += quantity
            self.save_listings()
            return True

    def remove_stock(self, listing_index, quantity):
        return self.add_stock(listing_index, -quantity)


    def get_all_listings(self):
        return self.listings
    
    def get_listing(self, index):
        return self.listings[index]


    def query_listings(self, name_segment: str, item_category: int, item_manufacturer: int):
        listings = list(self.listings)

        #remove all listings that do not match the manufacturer (if it is a search parameter)
        if item_manufacturer != -1:
            listings = [l for l in listings if l.manufacturer == item_manufacturer]

        #remove all listings that do not match the category (if it is a search parameter)
        if item_category != -1:
            listings = [l for l in listings if l.category == item_category]

        #any listing that does not contain the name segment should be discarded
        cleaned_segment = name_segment.strip()
        if cleaned_segment != "":
            listings = [l for l in listings if name_segment.lower() in l.name.lower()]

        
        #sort the remaining listings by name, alphabetically. (Insertion sort)
        for index in range(1, len(listings)):
            current_index = index
            swapped_listing = listings[index]

            while current_index > 0 and listings[current_index - 1].name > swapped_listing.name:
                listings[current_index] = listings[current_index - 1]
                current_index -= 1

            listings[current_index] = swapped_listing 
            
        return listings

class ListingManager:
    __instance = None


    @staticmethod
    def initialise(manifest_path = None):
        if manifest_path == None:
            manifest_path = ConfigManager.get_config_value("listings manifest")[1]

        category_file =  ConfigManager.get_config_value("listing categories file")[1]
        manufacturer_file =  ConfigManager.get_config_value("listing manufacturers file")[1]

        Listing.parse_categories(category_file)
        Listing.parse_manufacturers(manufacturer_file)
        ListingManager.__instance = _ListingManagerInstance(manifest_path)


    #ensures that an instance of the listing manager exists before running the wrapped function
    def check_exists(f):

        @wraps(f)
        def wrapper(*args, **kwargs):
            if ListingManager.__instance == None:
                ListingManager.initialise()

            return f(*args, **kwargs)

        return wrapper
    

    @staticmethod
    @check_exists
    def create_listing(name, desc, category, manufacturer):
        return ListingManager.__instance.create_listing(name, desc, category, manufacturer)
    
    @staticmethod
    @check_exists
    def update_listing(index, new_name, new_description, new_category, new_manufacturer):
        return ListingManager.__instance.update_listing(index, new_name, new_description, new_category, new_manufacturer)
    
    @staticmethod
    @check_exists
    def remove_listing(listing_index):
        return ListingManager.__instance.remove_listing(listing_index)
    
    @staticmethod
    @check_exists
    def get_listing_index(name):
        return ListingManager.__instance.get_listing_index(name)

    @staticmethod
    @check_exists
    def add_stock(listing, quantity):
        return ListingManager.__instance.add_stock(listing, quantity)
    
    @staticmethod
    @check_exists
    def remove_stock(listing, quantity):
        return ListingManager.__instance.remove_stock(listing, quantity)
    

    @staticmethod
    @check_exists
    def get_all_listings():
        return ListingManager.__instance.get_all_listings()
    
    @staticmethod
    @check_exists
    def get_listing(index):
        return ListingManager.__instance.get_listing(index)
    
    @staticmethod
    @check_exists
    def query_listings(name_segment, item_category, item_manufacturer):
        return ListingManager.__instance.query_listings(name_segment, item_category, item_manufacturer)
