import argparse
import sys
import configparser

from aiohttp import web

from website import Website
from listingmanager import ListingManager



def main(args, config):
    #pre-initialise the listing manager so it is ready as needed 
    ListingManager.initialise(config)

    #create the website server
    app = Website(args.templates_path)

    #start the website
    web.run_app(app)

if __name__ == "__main__":
    #get the config values which also have command line arguments
    config = configparser.ConfigParser()
    config.read("Resources/config.cfg")

    jinja_path = config.get("Operation", "JinjaTemplatesPath")
    hostname = config.get("Website", "Hostname")
    port = config.get("Website", "Port")

    #parse command line arguments. any provided will take priority over the config values
    parser = argparse.ArgumentParser(
                    prog='Inventory Manager',
                    description='Hosts a web interface and local dashboard for managing stock inventory.',
                    )
    parser.add_argument("--templates-path", default=jinja_path)
    parser.add_argument("--host", default=hostname)
    parser.add_argument("--port", default=port)
    args = parser.parse_args()

    if len(sys.argv) > 1: #we still accept one argument as main.py must be passed to python
        print(len(sys.argv))
        print("[[WARNING]] - Command-line arguments have been provided. These will override values in config.cfg!")

    #don't show an error to the console when ending the application at the command line
    try:
        main(args, config)
    except KeyboardInterrupt:
        quit(0)