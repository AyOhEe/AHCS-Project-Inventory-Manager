import asyncio


from dashboard import Dashboard
from website import Website

#time between tkinter window updates
WINDOW_UPDATE_DELAY = 0.02


loop_exit_trigger = False
async def main():
    global loop_exit_trigger


    #create the dashboard window
    window = Dashboard()

    #create the website server
    app = Website("Jinja templates/")


    #used to exit the website and window loop, clean up and then quit the program
    def cleanup():
        global loop_exit_trigger
        loop_exit_trigger = True

    
    #start the website
    await app.start_website("localhost", 8080)


    #call cleanup when the tkinter window is closed
    window.protocol("WM_DELETE_WINDOW", cleanup)

    #update loop to let asyncio event loop run while also updating the tkinter window
    while not loop_exit_trigger:
        window.update()
        await asyncio.sleep(WINDOW_UPDATE_DELAY)

    #before exiting the program, clean up the web server
    await app.destroy_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        quit(0)