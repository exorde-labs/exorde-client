"""
Scraper.py uses a scraping modules and pushes it's results - it contains
a versioning api which allows the orchestrator to change it's configuration.
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
