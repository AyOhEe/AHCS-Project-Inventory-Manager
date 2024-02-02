import json


from typing import Optional


#TODO encapsulation
class Listing:
    categories = {0: "Unsorted"}

    def __init__(
            self, 
            name: str = "New Stock Item", 
            description: str = "N/A", 
            category: Optional[str] = None,
            manufacturer: str = "Manufacturer not listed",
            quantity: int = 0
            ):
        self.name = name
        self.description = description
        self.manufacturer = manufacturer
        self.quantity = quantity

        #if no category is provided, default to "Unsorted"
        if category != None:
            self.category = category
        else:
            self.category = Listing.categories[0]

    def __str__(self) -> str:
        return f"<Listing: {self.quantity}*\"{self.manufacturer} :: {self.name}\" - {self.category}>"

    @classmethod
    def parse_categories(self, file="categories.txt"):
        try:
            with open(file, "r") as f:
                for line in f:
                    category = line.strip()
                    if category == "":
                        continue

                    if category in self.categories.values():
                        continue

                    index = len(self.categories)
                    self.categories[index] = category
        except FileNotFoundError:
            print(f"Listing: could not find \"{file}\"!")

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
            listing_data["category"] = Listing.categories[index]

        return Listing(**listing_data), True

if __name__ == "__main__":   
    Listing.parse_categories()
    print(Listing.categories)