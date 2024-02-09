import json
import traceback
import pathlib
import os


from functools import wraps


from . import Listing
from configmanager import ConfigManager


class _ListingManagerInstance:
    def __init__(self, listings_manifest = "listings/manifest.json"):
        #attempt to read the manifest
        try: 
            with open(listings_manifest, "r") as f:
                manifest = json.load(f)
        except FileNotFoundError:
            #TODO log error
            print(f"ListingManager: Unable to find listing manifest at \"{listings_manifest}\"")
            return
        
        #ensure that the manifest is valid
        if not "listings" in manifest:
            #TODO log error
            print(f"ListingManager: \"{listings_manifest}\" does not contain a \"listings\" entry!")

        #attempt to parse each listing
        self.parse_listings(manifest, listings_manifest)

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
                #TODO log error
                print(f"ListingManager: Error opening file \"{file_name}\" found in manifest. Skipping...")
            
            except json.JSONDecodeError as jde:
                #TODO log error
                print(f"ListingManager: Error parsing file \"{file_name}\" found in manifest. Skipping...")
                traceback.print_exc()
        

    def save_listings(self):
        #prepare the listings manifest and save each listing as we go
        listings_manifest = {"listings" : []}

        for l in self.listings:
            #store the filename so it can be retrieved later
            name_hash = hash(l.name)
            filename = f"{name_hash}.json"
            listings_manifest["listings"].append(filename)

            #open and save to each file
            path = os.path.join(self.directory, filename)
            try:
                with open(path, "w") as f:
                    json.dump(l.as_dict(), f)
            except FileNotFoundError:
                #TODO log error
                print("Could not open listing file {path}")


        try:
            with open(ConfigManager.get_config_value("listings manifest")[1], "w") as f:
                json.dump(listings_manifest, f)
        except FileNotFoundError:
            #TODO log error
            print("Could not open listings manifest to save. This should not occur.")

    def create_listing(self, name, desc, category, manufacturer):
        #enforce uniqueness
        for l in self.listings:
            if l.name == name:
                return False, f"Name must be unique. \"{name}\" was already listed."

        self.listings.append(Listing(name, desc, category, manufacturer, 0))
        self.save_listings()
        return True, None

    def update_listing(self):
        self.save_listings()
        pass

    def remove_listing(self):

        #TODO this needs to delete a file and remove the listing, it does not
        #     need to save listings
        pass


    def add_stock(self, listing, quantity):
        pass
    def remove_stock(self, listing, quantity):
        pass


    def get_all_listings(self):
        return self.listings


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
    def update_listing(*args, **kwargs):
        return ListingManager.__instance.update_listing(*args, **kwargs)
    
    @staticmethod
    @check_exists
    def remove_listing(*args, **kwargs):
        return ListingManager.__instance.remove_listing(*args, **kwargs)


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
    def query_listings(name_segment, item_category, item_manufacturer):
        return ListingManager.__instance.query_listings(name_segment, item_category, item_manufacturer)
    
if __name__ == "__main__":
    ListingManager.initialise()