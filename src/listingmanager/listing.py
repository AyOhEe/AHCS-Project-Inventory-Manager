import json


from typing import Optional


#TODO encapsulation
class Listing:
    categories = {0: "Unsorted"}
    manufacturers = {0 : "Manufacturer not listed"}

    def __init__(
            self, 
            name: str = "New Stock Item", 
            description: str = "N/A", 
            category: Optional[str] = None,
            manufacturer: str = None,
            quantity: int = 0
            ):
        self.name = name
        self.description = description
        self.manufacturer = manufacturer
        self.quantity = quantity

        #if no category is provided, use the default
        if category != None:
            self.category = category
        else:
            self.category = Listing.categories[0]

        #if no manufacturer is provided, use the default
        if manufacturer != None:
            self.manufacturer = manufacturer
        else:
            self.manufacturer = Listing.manufacturers[0]

    def __str__(self) -> str:
        return f"<Listing: {self.quantity}*\"{self.manufacturer} :: {self.name}\" - {self.category}>"

    @classmethod
    def parse_categories(cls, file="listings/categories.txt"):
        try:
            with open(file, "r") as f:
                for line in f:
                    category = line.strip()
                    if category == "":
                        continue

                    if category in cls.categories.values():
                        continue

                    index = len(cls.categories)
                    cls.categories[index] = category
        except FileNotFoundError:
            print(f"Listing: could not find \"{file}\"!")
    
    @classmethod
    def parse_manufacturers(cls, file="listings/manufacturers.txt"):
        try:
            with open(file, "r") as f:
                for line in f:
                    manufacturer = line.strip()
                    if manufacturer == "":
                        continue

                    if manufacturer in cls.manufacturers.values():
                        continue

                    index = len(cls.manufacturers)
                    cls.manufacturers[index] = manufacturer
        except FileNotFoundError:
            print(f"Listing: could not find \"{file}\"!")

    #TODO this error handling sucks
    @staticmethod 
    def from_file(file_obj):
        listing_data = json.load(file_obj)

        #replace the category index with the category name
        if "category" in listing_data:
            try:
                index = int(listing_data["category"])
            except ValueError:
                #TODO log error
                print("Listing from_file: \"category\" should be a whole (>= 0) number!")
                return None, False

        if "manufacturer" in listing_data:
            try:
                index = int(listing_data["manufacturer"])
            except ValueError:
                #TODO log error
                print("Listing from_file: \"manufacturer\" should be a whole (>= 0) number!")
                return None, False

        return Listing(**listing_data), True

if __name__ == "__main__":   
    Listing.parse_categories()
    print(Listing.categories)
    Listing.parse_manufacturers()
    print(Listing.manufacturers)