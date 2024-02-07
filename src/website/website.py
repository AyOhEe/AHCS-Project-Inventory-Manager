import asyncio
import aiohttp_jinja2
import jinja2
import os


from functools import wraps
from datetime import datetime
from aiohttp import web


from pinmanager import PinManager
from listingmanager import Listing, ListingManager
from configmanager import ConfigManager


#this massive decorator means that for a new page to verify a PIN, one only need
#use this decorator and it will handle the redirects for you if given an invalid PIN.
def verifies_pin(requires_admin=False):

    def decorator(request_handler):
        @wraps(request_handler)
        async def wrapper(self, request, *args, **kwargs):
            params = await request.post()

            if "PIN" in params:
                pin = params["PIN"]

                if PinManager.verify_pin(pin, requires_admin):
                    return await request_handler(self, request, *args, **kwargs)
                else:
                    #TODO log authentication error
                    raise web.HTTPFound('/auth_error?reason=invalidpin')
            else:
                #TODO log authentication eror
                raise web.HTTPFound('/auth_error?reason=nopin')
            
        return wrapper

    #decorators which can take arguments need to return another decorator.
    return decorator



class Website(web.Application):
    def __init__(self, templates_path, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug_mode = debug
        
        #TODO sub applications? - this class is massive
        aiohttp_jinja2.setup(self, loader=jinja2.FileSystemLoader(templates_path))
        routes = [
            web.get('/', self.g_index),



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



            web.get('/auth_error', self.g_auth_error),
            web.get('/generic_error', self.g_generic_error),


            web.get('/data/listing_categories.json', self.g_listing_categories),
            web.get('/data/listing_manufacturers.json', self.g_listing_manufacturers),
        ]

        debug_routes = [
            web.get('/debug/listing_data', self.__g_listing_data),
            web.get('/debug/all_listings', self.__g_all_listings),
        ]
        if self.debug_mode:
            routes += debug_routes

        #we can't serve static resources just by accepting a path to them - that would
        #require sanitation, and it can't be trusted to be perfect. by checking for all
        #the resources we should serve at initialisation, we take that risk away entirely.
        routes += self.process_static_resources()

        self.add_routes(routes)
    
    async def start_website(self, host_addr, port):
        #create the aiohttp application runner used to run tkinter and aiohttp concurrently
        self.runner = web.AppRunner(self)
        await self.runner.setup()
        site = web.TCPSite(self.runner, host_addr, port)
        await site.start() #the web server now runs in the background

    async def destroy_server(self):
        await self.runner.cleanup()


    def process_static_resources(self):
        routes = []
        directory = ConfigManager.get_config_value('static web directory')[1]
        for subdir, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(subdir, file)
                webpath = "/static/" + filepath[len(directory):]
                print(f"Website: Found static web file {filepath}. Serving at {webpath}")
                routes.append(self.serve_static(filepath, webpath))

        return routes
    
    def serve_static(self, filepath, webpath):
        def g_static_resource(request):
            return web.FileResponse(filepath)

        return web.get(webpath, g_static_resource)


    #region Pages
    
    async def g_index(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
                                                request,
                                                context)
        return response

    
    async def g_search(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
                                                request,
                                                context)
        return response
    
    async def g_search_results(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
                                                request,
                                                context)
        return response


    async def g_remove_stock(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
                                                request,
                                                context)
        return response
    
    @verifies_pin()
    async def p_stock_removed(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
                                                request,
                                                context)
        return response
    

    async def g_add_stock(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
                                                request,
                                                context)
        return response
    
    @verifies_pin()
    async def p_stock_added(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
                                                request,
                                                context)
        return response
    

    async def g_create_listing(self, request):
        context = { 
            "categories" : Listing.categories, 
            "manufacturers" : Listing.manufacturers 
        }
        response = aiohttp_jinja2.render_template('create_listing.html',
                                                request,
                                                context)
        return response
    
    @verifies_pin(requires_admin = True)
    async def p_listing_created(self, request):
        #extract the listing details from the request
        print(await request.post())
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
        response = aiohttp_jinja2.render_template('listing_created.html',
                                                request,
                                                context)
        return response
    

    async def g_remove_listing(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
                                                request,
                                                context)
        return response
    
    @verifies_pin(requires_admin = True)
    async def p_listing_removed(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
                                                request,
                                                context)
        return response
    

    async def g_update_listing(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
                                                request,
                                                context)
        return response
    
    @verifies_pin(requires_admin = True)
    async def p_listing_updated(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
                                                request,
                                                context)
        return response
    

    async def g_auth_error(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
                                                request,
                                                context)
        return response
    
    async def g_generic_error(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
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
        response = aiohttp_jinja2.render_template('listing_data.html',
                                                request,
                                                context)
        return response
    
    async def __g_all_listings(self, request):
        context = {
            "listings" : [str(l) for l in ListingManager.get_all_listings()]
        }
        response = aiohttp_jinja2.render_template('all_listings.html',
                                                request,
                                                context)
        return response
    #endregion