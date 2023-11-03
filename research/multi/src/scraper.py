"""
Scraper.py uses a scraping modules and pushes it's results.
"""
# scraper.py
import argparse
import asyncio
from aiohttp import web, ClientSession
import subprocess
import pkg_resources
import sys

class Scraper:
    def __init__(self):
        self.is_active = False  # Controls whether the scraper is active or not
    
    async def start_scraping(self):
        self.is_active = True
        async for data in self.data_generator():
            if not self.is_active: 
                break
            await self.push_data(data)
    
    def stop_scraping(self):
        self.is_active = False

    async def data_generator(self):
        # This is your async generator that yields data
        while self.is_active:
            # Scrape data here and yield it
            data = "some scraped data"
            yield data
            await asyncio.sleep(1)  # Simulate async operation delay
    
    async def push_data(self, data):
        """
        Pushing data should not be blocking
        """
        async with ClientSession() as session:
            # Assuming that 'data' is a dictionary that can be turned into JSON
            async with session.post('http://127.0.0.1:8081/add', json=data) as response:
                response_data = await response.text()  # Or use response.json() for JSON response
                print(f"Status: {response.status}")
                print(f"Response: {response_data}")


def stop_scraping(request):
    # Cancel the scraper task
    scraper_task = request.app.get('scraper_task')
    if scraper_task:
        scraper_task.cancel()
        request.app['scraper'].stop_scraping()


async def start(request):
    # Create a task for the scraper to run in the background
    request.app['scraper_task'] = asyncio.create_task(request.app['scraper'].start_scraping())
    return web.Response(text="Scraper started")


async def stop(request):
    stop_scraping(request)
    return web.Response(text="Scraper stopped")


async def install_module(module_name, target_version):
    """
    Install or update the specified module using pip in a subprocess.
    This function assumes that the module name and version are validated and safe to use.
    """
    # Build the package specification with the version if specified
    package_spec = f"{module_name}=={target_version}" if target_version else module_name

    # Execute the pip install command
    process = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "pip", "install", package_spec,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        # If the command failed, raise an exception with the stderr output
        raise Exception(stderr.decode().strip())
    return stdout.decode().strip()


async def update_module_background(module_name, target_version):
    """
    A background task to update the module and exit the server.
    """
    try:
        await install_module(module_name, target_version)
        os._exit(0)  # Exits the process, causing the server to stop.
    except Exception as e:
        print(f"An error occurred during module installation: {e}")


async def install_module(request):
    """
    Endpoint to install or update a module.
    Starts the update in the background and returns immediately.
    """
    # Extract module name and version from the request query parameters
    module_name = request.query.get('module')
    target_version = request.query.get('version')

    if not module_name:
        return web.Response(text="Module name is required", status=400)

    # Start the update in a background task
    asyncio.create_task(update_module_background(module_name, target_version))


async def status_set(request):
    """
    used by blade.py on status_set (basicly a super)

    This should make sure that the current consumer is an instance of the correct
    module and version
    """
    details = await request.json()
    print('super status set {}'.format(details))
    return web.json_response(request.app['node'])

app = web.Application()
app['scraper'] = Scraper()
app['status_set'] = status_set
