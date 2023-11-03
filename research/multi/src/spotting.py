"""
Spotting server waits to receive data, accumulates it and applies batch logic
on it

"""
from aiohttp import web
import asyncio

# Shared state and lock
shared_data = {'items': []}
lock = asyncio.Lock()

# Maximum size of the list before processing
MAX_SIZE = 10

# This could be any function that processes your data
async def process_data(data):
    # Replace with the actual processing you need to do
    print("Processing data:", data)
    await asyncio.sleep(1)  # Simulate some processing time

async def add_data(request):
    """
    Scrapers push items trough this endpoint
    """
    data = await request.text()
    
    async with lock:
        shared_data['items'].append(data)
        data_size = len(shared_data['items'])
        
        # If the list reaches MAX_SIZE, trigger processing
        if data_size >= MAX_SIZE:
            # Copy the data for processing and clear the shared state
            data_to_process = shared_data['items'].copy()
            shared_data['items'] = []
            # Run the data processing without holding the lock
            asyncio.create_task(process_data(data_to_process))
            return web.Response(
                text=f"Data added and processing triggered with {data_size} items."
            )

    return web.Response(text="Data added.")

app = web.Application()
app.router.add_post('/add', add_data)
