import json
import traceback
import pathlib
import os


from functools import wraps


from listing import Listing


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
        
        for listing in self.listings:
            print(listing)

    def parse_listings(self, manifest, manifest_path):
        self.listings = []
        directory = pathlib.Path(os.getcwd()).joinpath(pathlib.Path(manifest_path))
        directory = pathlib.Path(os.path.join(*directory.parts[:-1]))
        for file_name in manifest["listings"]:
            try:
                with open(os.path.join(directory, file_name), "r") as f:
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
        

    def create_listing(self):
        pass
    def update_listing(self):
        pass
    def remove_listing(self):
        pass


    def add_stock(self, listing, quantity):
        pass
    def remove_stock(self, listing, quantity):
        pass


    #query listings?

class ListingManager:
    __instance = None


    @staticmethod
    def initialise(manifest_path = "listings/manifest.json"):
        Listing.parse_categories()
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
    def create_listing():
        return ListingManager.__instance.create_listing()
    
    @staticmethod
    @check_exists
    def update_listing():
        return ListingManager.__instance.update_listing()
    
    @staticmethod
    @check_exists
    def remove_listing():
        return ListingManager.__instance.remove_listing()


    @staticmethod
    @check_exists
    def add_stock(listing, quantity):
        return ListingManager.__instance.add_stock(listing, quantity)
    
    @staticmethod
    @check_exists
    def remove_stock(listing, quantity):
        return ListingManager.__instance.remove_stock(listing, quantity)
    
if __name__ == "__main__":
    ListingManager.initialise()