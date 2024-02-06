async function asyncMain(){
    var listingCategories = await getListingCategories();
    var listingManufacturers = await getListingManufacturers();

    console.log(listingCategories);
    console.log(listingManufacturers);
}

asyncMain();