import json


from typing import Optional, TextIO, Tuple


#record type
class Listing:
    categories = {0: "Unsorted"}
    manufacturers = {0 : "Manufacturer not listed"}

    def __init__(
            self, 
            name: str = "New Stock Item", 
            description: str = "N/A", 
            category: int = 0,
            manufacturer: int = 0,
            quantity: int = 0,
            _force_construct: bool = False #this should never be used in production.
            ):                             #it exists only for use in testing.
        if not _force_construct:
            if name.strip() == "":
                raise ValueError("Name cannot be blank or similar.")
            if not isinstance(manufacturer, int) or manufacturer < 0:
                raise ValueError("Manufacturer must be greater than zero")
            if not isinstance(category, int) or category < 0:
                raise ValueError("Category must be greater than zero")
            if not isinstance(quantity, int) or quantity < 0:
                raise ValueError("Quantity must be greater than zero")

        self.name = name.strip()
        self.description = description
        self.manufacturer = manufacturer
        self.quantity = quantity
        self.category = category

    def __str__(self) -> str:
        return f"Listing: {self.quantity}*\"{Listing.manufacturers[self.manufacturer]} :: {self.name}\" - {Listing.categories[self.category]}" \
            +f"\n         {self.description[:30]}"
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Listing):
            return (self.name == __value.name) \
            and (self.description == __value.description) \
            and (self.category == __value.category) \
            and (self.manufacturer == __value.manufacturer) \
            and (self.quantity == __value.quantity)
        
        return False
    
    def __ne__(self, __value: object) -> bool:
        return not self == __value

    def as_dict(self) -> dict:
        return {
            "name" : self.name,
            "description" : self.description,
            "category" : self.category,
            "manufacturer" : self.manufacturer,
            "quantity" : self.quantity
        }

    @classmethod
    def parse_categories(cls, file: str="listings/categories.txt") -> None:
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
    def parse_manufacturers(cls, file: str="listings/manufacturers.txt") -> None:
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

    @staticmethod 
    def from_file(file_obj: TextIO) -> Tuple[Optional['Listing'], bool]:
        listing_data = json.load(file_obj)
        return Listing(**listing_data), True