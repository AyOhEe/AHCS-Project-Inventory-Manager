import asyncio


from dashboard import Dashboard
from website import Website
from pinmanager import PinManager

#time between tkinter window updates
WINDOW_UPDATE_DELAY = 0.1


#directory containing the website page templates
TEMPLATES_PATH = "Jinja templates/"
#address at which the website hosts itself
HOST_ADDRESS = "0.0.0.0"
#port which the website hosts itself
PORT = 8080


async def main():
    #create the dashboard window
    window = Dashboard()
    #create the website server
    app = Website(TEMPLATES_PATH)

    #start the website in the background
    await app.start_website(HOST_ADDRESS, PORT)

    #start the dashboard window's loop. 
    #tk.Tk.mainloop is not used as it blocks the main thread, 
    #blocking asyncio, blocking the website
    await window.async_mainloop(WINDOW_UPDATE_DELAY)

    #before exiting the program, clean up the web server
    await app.destroy_server()

if __name__ == "__main__":
    #don't show an error to the console when ending the application at the command line
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        quit(0)