import asyncio
import tkinter as tk
import aiohttp_jinja2
import jinja2

from datetime import datetime
from aiohttp import web

#time between tkinter window updates
WINDOW_UPDATE_DELAY = 0.02


async def hello(request):
    context = {'datetime' : str(datetime.now())}
    response = aiohttp_jinja2.render_template('hello.html',
                                              request,
                                              context)
    return response


loop_exit_trigger = False
async def main():
    global loop_exit_trigger


    #configure the tkinter window for the dashboard
    window = tk.Tk()

    #configure the aiohttp application for the website front end with jinja for templates
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('Jinja templates/'))
    app.add_routes([web.get('/', hello)])


    #used to exit the website and window loop, clean up and then quit the program
    def cleanup():
        global loop_exit_trigger
        loop_exit_trigger = True

    
    #create the aiohttp application runner used to run tkinter and aiohttp concurrently
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()


    #call cleanup when the tkinter window is closed
    window.protocol("WM_DELETE_WINDOW", cleanup)

    #update loop to let asyncio event loop run while also updating the tkinter window
    while not loop_exit_trigger:
        window.update()
        await asyncio.sleep(WINDOW_UPDATE_DELAY)

    #before exiting the program, clean up the aiohttp server
    await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())