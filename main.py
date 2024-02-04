import asyncio
import argparse
import sys


from dashboard import Dashboard
from website import Website
from pinmanager import PinManager
from listingmanager import ListingManager



async def main(args):
    #TODO don't really like this but what alternative?
    #initialise the listing manager before its first use so it's ready beforehand
    ListingManager.initialise()


    #create the dashboard window
    window = Dashboard(debug=args.debug)
    #create the website server
    app = Website(args.templates_path, debug=args.debug)

    #start the website in the background
    await app.start_website(args.host, args.port)

    #start the dashboard window's loop. 
    #tk.Tk.mainloop is not used as it blocks the main thread, 
    #blocking asyncio, blocking the website
    await window.async_mainloop(args.refresh_rate)

    #before exiting the program, clean up the web server
    await app.destroy_server()

if __name__ == "__main__":

    #parse command line arguments. any provided will take priority over the config values
    #TODO replace config values
    parser = argparse.ArgumentParser(
                    prog='Inventory Manager',
                    description='Hosts a web interface and local dashboard for managing stock inventory.',
                    )
    parser.add_argument("--debug", default=False, action='store_true') #debug flag
    parser.add_argument("--templates-path", default="Jinja templates/")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=8080)
    parser.add_argument("--refresh-rate", default=0.1)
    args = parser.parse_args()

    if args.debug:
        print("[[WARNING]] - Running in debug mode. Do not use this in production!")
    if len(sys.argv) > 1: #we still accept one argument as main.py must be passed to python
        print(len(sys.argv))
        print("[[WARNING]] - Command-line arguments have been provided. These will override values in config.cfg!")

    #don't show an error to the console when ending the application at the command line
    try:
        asyncio.run(main(args), debug=args.debug)
    except KeyboardInterrupt:
        quit(0)