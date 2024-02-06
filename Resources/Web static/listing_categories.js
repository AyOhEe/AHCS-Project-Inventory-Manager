async function getListingCategories() {
    var resp = (await fetch("/data/listing_categories.json")).json();
    return resp;
}