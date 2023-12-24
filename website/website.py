import asyncio
import aiohttp_jinja2
import jinja2


from functools import wraps
from datetime import datetime
from aiohttp import web


from pinmanager import PinManager


#this massive decorator means that for a new page to verify a PIN, one only need
#use this decorator and it will handle the redirects for you if given an invalid PIN.
def verifies_pin(request_handler, needs_admin=False):

    @wraps(request_handler)
    async def wrapper(self, request, *args, **kwargs):
        params = await request.post()

        if "PIN" in params:
            pin = params["PIN"]

            if PinManager.verify_pin(pin, needs_admin):
                return await request_handler(self, request, *args, **kwargs)
            else:
                #TODO log authentication error
                raise web.HTTPFound('/auth_error?reason=invalidpin')
        else:
            #TODO log authentication eror
            raise web.HTTPFound('/auth_error?reason=nopin')

    return wrapper



class Website(web.Application):
    def __init__(self, templates_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        aiohttp_jinja2.setup(self, loader=jinja2.FileSystemLoader(templates_path))
        self.add_routes([
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
        ])
    
    async def start_website(self, host_addr, port):
        #create the aiohttp application runner used to run tkinter and aiohttp concurrently
        self.runner = web.AppRunner(self)
        await self.runner.setup()
        site = web.TCPSite(self.runner, host_addr, port)
        await site.start() #the web server now runs in the background

    async def destroy_server(self):
        await self.runner.cleanup()


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
    
    @verifies_pin
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
    
    @verifies_pin
    async def p_stock_added(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
                                                request,
                                                context)
        return response
    

    async def g_create_listing(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
                                                request,
                                                context)
        return response
    
    @verifies_pin(requires_admin = True)
    async def p_listing_created(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('index.html',
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
    #endregion