"""
A blade is a generic aiohttp server wrapper that insure different endpoints on 
each blades.

Think of this as a class which blades inherit from (spotting or scrapper)
"""

import os
import argparse
import asyncio
from aiohttp import web
import json
import logging

async def hello(request):
    return web.Response(text="Hello, World!")

async def kill(request):
    os._exit(-1)


"""
here blade is 1 blade configuration eg

  - name: scraper_one
    blade: scraper
    managed: true
    host: 127.0.0.1
    port: 8002
    venv: "./venvs/scraper_one"

weheras topology is the complete configuration file

"""

async def start_blade(blade, topology):
    # If params are provided, set them in the app's shared state
    app['topology'] = topology
    app['blade'] = blade
    await web._run_app(app, host=blade['host'], port=blade['port'])

async def static_cluster_parameters(request):
    """
    Defined by the user trough the topology yaml configuration file
    """
    return web.json_response(request.app['static_cluster_parameters'])

async def status(request):
    """get only version of below function"""
    return web.json_response(request.app['blade'])


async def status_set(request):
    """
    The status endpoint is used by the orchestrator to inform intent and retrieve
    status of blade's
        - type
        - configuration
        - status
    """
    intent = await request.json()
    if request.app.get('status_set', None):
        try:
            # we define the interface using request.app internal dict 
            return await request.app['status_set'](request)
        except:
            pass
    # if there is no overwrite we simply return the blade's status
    return web.json_response(request.app['blade'])

"""
Overclassing the blades is done by importing their app definition and overwriting
it here.

Each blade should be launched using this script.
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generic aiohttp server manager")
    parser.add_argument("--blade", type=json.loads, default={}, help="JSON string of blade configuration")
    parser.add_argument("--topology", type=json.loads, default={}, help="JSON string of topology")
    args = parser.parse_args()

    # Dynamically load the appropriate aiohttp app from the subblade
    mod = __import__(args.blade['blade'], fromlist=['app'])
    app = getattr(mod, 'app')
    app.router.add_get('/', hello)
    app.router.add_get('/kill', kill)
    app.router.add_get('/static', static_cluster_parameters)
    app.router.add_get('/status', status)
    app.router.add_post('/status', status_set)

    asyncio.run(start_blade(args.blade, args.topology))
