async function getListingManufacturers() {
    var resp = (await fetch("/data/listing_manufacturers.json")).json();
    return resp;
}