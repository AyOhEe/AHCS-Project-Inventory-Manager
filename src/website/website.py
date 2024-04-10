import asyncio
import aiohttp_jinja2
import jinja2
import os


from functools import wraps
from datetime import datetime
from aiohttp import web


from listingmanager import Listing, ListingManager


class Website(web.Application):
    def __init__(self, templates_path, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug_mode = debug
        
        aiohttp_jinja2.setup(self, loader=jinja2.FileSystemLoader(templates_path))
        routes = [
            web.get('/', self.g_index),
            web.get('/help', self.g_help),


            web.get('/search', self.g_search),
            web.get('/search_results', self.g_search_results),

            web.get('/remove_stock', self.g_remove_stock),
            web.post('/stock_removed', self.p_stock_removed),

            web.get('/add_stock', self.g_add_stock),
            web.post('/stock_added', self.p_stock_added),


            web.get('/create_listing', self.g_create_listing),
            web.post('/listing_created', self.p_listing_created),

            web.get('/remove_listing', self.g_remove_listing),
            web.post('/listing_removed', self.p_listing_removed),

            web.get('/update_listing', self.g_update_listing),
            web.post('/listing_updated', self.p_listing_updated),


            web.get('/data/listing_categories.json', self.g_listing_categories),
            web.get('/data/listing_manufacturers.json', self.g_listing_manufacturers),
        ]

        debug_routes = [
            web.get('/debug/listing_data', self.__g_listing_data),
            web.get('/debug/all_listings', self.__g_all_listings),
        ]
        if self.debug_mode:
            routes += debug_routes

        self.add_routes(routes)


    #region Pages
    
    async def g_index(self, request):
        context = dict()
        response = aiohttp_jinja2.render_template('index.html.j2',
                                                request,
                                                context)
        return response

    async def g_help(self, request):
        context = dict()
        response = aiohttp_jinja2.render_template('help.html.j2',
                                                request,
                                                context)
        return response
    
    async def g_search(self, request):
        context = { 
            "categories" : Listing.categories, 
            "manufacturers" : Listing.manufacturers 
        }
        response = aiohttp_jinja2.render_template('search.html.j2',
                                                request,
                                                context)
        return response
    
    async def g_search_results(self, request):
        #extract the search parameters from the request url
        try:
            item_name = request.query["item_name"]
            item_category = int(request.query["item_category"])
            item_manufacturer = int(request.query["item_manufacturer"])
        except KeyError:
            raise web.HTTPBadRequest(reason="Search parameters not supplied")
        except ValueError:
            raise web.HTTPBadRequest(reason="Non-integer value passed where integer required    ")
        
        results = ListingManager.query_listings(item_name, item_category, item_manufacturer)


        category_name = Listing.categories[item_category] if item_category != -1 else "Any Category"
        manufacturer_name = Listing.manufacturers[item_manufacturer] if item_manufacturer != -1 else "Any Manufacturer"
        context = { 
            "param_item_name" : item_name, 
            "param_item_category" : category_name,
            "param_item_manufacturer" : manufacturer_name,
            "categories" : Listing.categories, 
            "manufacturers" : Listing.manufacturers,
            "results" : [l.as_dict() for l in results] 
        }
        response = aiohttp_jinja2.render_template('search_results.html.j2',
                                                request,
                                                context)
        return response


    async def g_remove_stock(self, request):
        #extract the name 
        try:
            name = request.rel_url.query["item_name"]

        except KeyError:
            #missing values. can't create the listing!
            #TODO respond with proper error
            raise web.HTTPBadRequest(reason="Incomplete request")
        
        context = {"item_name" : name}
        response = aiohttp_jinja2.render_template('remove_stock.html.j2',
                                                request,
                                                context)
        return response
    
    async def p_stock_removed(self, request):
        #extract the name and change in quantity
        params = await request.post()
        try:
            name = params["item_name"]
            quantity = int(params["quantity"])

        except KeyError:
            #missing values. can't create the listing!
            #TODO respond with proper error
            raise web.HTTPBadRequest(reason="Incomplete request")
        
        except ValueError:
            #non-integer category or manufacturer
            #TODO respond with proper error
            raise web.HTTPBadRequest(reason="Non-integer where integer expected")
        
        index = ListingManager.get_listing_index(name)
        if index == -1:
            raise web.HTTPBadRequest(reason="Listing does not exist")
        if not ListingManager.remove_stock(index, quantity):
            raise web.HTTPBadRequest(reason="Insufficient stock")

        context = dict()
        response = aiohttp_jinja2.render_template('stock_removed.html.j2',
                                                request,
                                                context)
        return response
    

    async def g_add_stock(self, request):
        #extract the name 
        try:
            name = request.rel_url.query["item_name"]

        except KeyError:
            #missing values. can't create the listing!
            #TODO respond with proper error
            raise web.HTTPBadRequest(reason="Incomplete request")
        
        context = {"item_name" : name}
        response = aiohttp_jinja2.render_template('add_stock.html.j2',
                                                request,
                                                context)
        return response
    
    async def p_stock_added(self, request):
        #extract the name and change in quantity
        request_json = await request.post()
        try:
            name = request_json["item_name"]
            quantity = int(request_json["quantity"])

        except KeyError:
            #missing values. can't create the listing!
            #TODO respond with proper error
            raise web.HTTPBadRequest(reason="Incomplete request")
        
        except ValueError:
            #non-integer category or manufacturer
            #TODO respond with proper error
            raise web.HTTPBadRequest(reason="Non-integer where integer expected")
        
        index = ListingManager.get_listing_index(name)
        if index == -1:
            raise web.HTTPBadRequest(reason="Listing does not exist")
        if not ListingManager.add_stock(index, quantity):
            raise web.HTTPBadRequest(reason="Insufficient stock")

        context = dict()
        response = aiohttp_jinja2.render_template('stock_added.html.j2',
                                                request,
                                                context)
        return response
    

    async def g_create_listing(self, request):
        context = { 
            "categories" : Listing.categories, 
            "manufacturers" : Listing.manufacturers 
        }
        response = aiohttp_jinja2.render_template('create_listing.html.j2',
                                                request,
                                                context)
        return response
    
    async def p_listing_created(self, request):
        #extract the listing details from the request
        request_json = await request.post()
        try:
            name = request_json["item_name"]
            description = request_json["item_description"]
            category = int(request_json["item_category"])
            manufacturer = int(request_json["item_manufacturer"])

        except KeyError:
            #missing values. can't create the listing!
            #TODO respond with proper error
            raise web.HTTPBadRequest(reason="Incomplete request")
        
        except ValueError:
            #non-integer category or manufacturer
            #TODO respond with proper error
            raise web.HTTPBadRequest(reason="Non-integer where integer expected")

        success, reason = ListingManager.create_listing(name, description, category, manufacturer)

        context = {
            "success" : success,
            "reason" : reason,
            "item_name" : name, 
            "item_description" : description, 
            "item_category" : Listing.categories[category],
            "item_manufacturer" : Listing.manufacturers[manufacturer]
        }
        response = aiohttp_jinja2.render_template('listing_created.html.j2',
                                                request,
                                                context)
        return response
    

    async def g_remove_listing(self, request):
        #extract the name 
        try:
            name = request.rel_url.query["item_name"]

        except KeyError:
            #missing values. can't create the listing!
            #TODO respond with proper error
            raise web.HTTPBadRequest(reason="Incomplete request")
        
        context = {"item_name" : name}
        response = aiohttp_jinja2.render_template('remove_listing.html.j2',
                                                request,
                                                context)
        return response
    
    async def p_listing_removed(self, request):
        #extract the name and change in quantity
        params = await request.post()
        try:
            name = params["item_name"]

        except KeyError:
            #missing values. can't create the listing!
            #TODO respond with proper error
            raise web.HTTPBadRequest(reason="Incomplete request")
        
        index = ListingManager.get_listing_index(name)
        if index == -1:
            raise web.HTTPBadRequest(reason="Listing does not exist")
        ListingManager.remove_listing(index)
        
        context = dict()
        response = aiohttp_jinja2.render_template('listing_removed.html.j2',
                                                request,
                                                context)
        return response
    

    async def g_update_listing(self, request):
        #extract the name 
        try:
            name = request.rel_url.query["item_name"]

        except KeyError:
            #missing values. can't create the listing!
            #TODO respond with proper error
            raise web.HTTPBadRequest(reason="Incomplete request")
        
        index = ListingManager.get_listing_index(name)
        if index == -1:
            raise web.HTTPBadRequest(reason="Listing does not exist")
        listing = ListingManager.get_listing(index)
        
        context = {
            "item_name" : name,
            "item_desc" : listing.description,
            "item_category" : listing.category,
            "item_manufacturer" : listing.manufacturer,
            "categories" : Listing.categories,
            "manufacturers" : Listing.manufacturers
        }
        response = aiohttp_jinja2.render_template('update_listing.html.j2',
                                                request,
                                                context)
        return response

    async def p_listing_updated(self, request):
        #extract the name and change in quantity
        params = await request.post()
        try:
            name = params["item_old_name"]
            new_name = params["item_new_name"]
            new_description = params["item_new_desc"]
            new_category = int(params["item_new_category"])
            new_manufacturer = int(params["item_new_manufacturer"])

        except KeyError:
            #missing values. can't create the listing!
            #TODO respond with proper error
            raise web.HTTPBadRequest(reason="Incomplete request")
        
        except ValueError:
            #non-integer category or manufacturer
            #TODO respond with proper error
            raise web.HTTPBadRequest(reason="Non-integer where integer expected")
        
        index = ListingManager.get_listing_index(name)
        if index == -1:
            raise web.HTTPBadRequest(reason="Listing does not exist")
        ListingManager.update_listing(index, new_name, new_description, new_category, new_manufacturer)
        
        context = dict()
        response = aiohttp_jinja2.render_template('listing_updated.html.j2',
                                                request,
                                                context)
        return response
    

    async def g_listing_categories(self, request):
        #TODO fix when Listing gets encapsulation
        return web.json_response(Listing.categories)

    async def g_listing_manufacturers(self, request):
        #TODO fix when Listing gets encapsulation
        return web.json_response(Listing.manufacturers)
    

    async def __g_listing_data(self, request):
        context = {
            "categories" : Listing.categories,
            "manufacturers" : Listing.manufacturers
        }
        response = aiohttp_jinja2.render_template('listing_data.html.j2',
                                                request,
                                                context)
        return response
    
    async def __g_all_listings(self, request):
        context = {
            "listings" : [str(l) for l in ListingManager.get_all_listings()]
        }
        response = aiohttp_jinja2.render_template('all_listings.html.j2',
                                                request,
                                                context)
        return response
    #endregion