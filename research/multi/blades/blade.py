"""
A blade is a generic aiohttp server wrapper that insure different endpoints on 
each modules.

Think of this as a class which modules inherit from (spotting or scrapper)
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

async def start_blade(blade, topology):
    # If params are provided, set them in the app's shared state
    app['topology'] = topology
    app['blade'] = blade
    await web._run_app(app, host=blade['host'], port=blade['port'])

async def parameters(request):
    return web.json_response(request.app['params'])

async def status(request):
    """get only version of below function"""
    return web.json_response(request.app['blade'])


async def status_set(request):
    """
    The status endpoint is used by the orchestrator to inform intent and retrieve
    status of blade
        - the module's type
        - the module configuration
        - the module status
    """
    intent = await request.json()
    if request.app.get('status_set', None):
        try:
            # we define overwrite using request.app internal dict
            return await request.app['status_set'](request)
        except:
            pass
    # if there is no overwrite we simply return the blade's status
    return web.json_response(request.app['blade'])

"""
Each server is wrapped by a blade, so launching a module should be done trough
the blade.py
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generic aiohttp server manager")
    parser.add_argument("--blade", type=json.loads, default={}, help="JSON string of blade configuration")
    parser.add_argument("--topology", type=json.loads, default={}, help="JSON string of topology")
    args = parser.parse_args()

    # Dynamically load the appropriate aiohttp app from the submodule
    mod = __import__(args.blade['module'], fromlist=['app'])
    app = getattr(mod, 'app')
    app.router.add_get('/', hello)
    app.router.add_get('/kill', kill)
    app.router.add_get('/parameters', parameters)
    app.router.add_get('/status', status)
    app.router.add_post('/status', status_set)

    asyncio.run(start_blade(args.blade, args.topology))
