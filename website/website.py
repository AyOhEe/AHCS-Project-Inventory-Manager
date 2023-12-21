import asyncio
import aiohttp_jinja2
import jinja2


from datetime import datetime
from aiohttp import web

class Website(web.Application):
    def __init__(self, templates_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        aiohttp_jinja2.setup(self, loader=jinja2.FileSystemLoader(templates_path))
        self.add_routes([web.get('/', self.hello)])

    async def hello(self, request):
        context = {'datetime' : str(datetime.now())}
        response = aiohttp_jinja2.render_template('hello.html',
                                                request,
                                                context)
        return response
    
    async def start_website(self, host_addr, port):
        #create the aiohttp application runner used to run tkinter and aiohttp concurrently
        self.runner = web.AppRunner(self)
        await self.runner.setup()
        site = web.TCPSite(self.runner, host_addr, port)
        await site.start() #the web server now runs in the background

    async def destroy_server(self):
        await self.runner.cleanup()

    