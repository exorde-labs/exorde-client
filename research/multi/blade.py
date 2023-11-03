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

async def start_blade(node, topology):
    # If params are provided, set them in the app's shared state
    app['topology'] = topology
    app['node'] = node
    await web._run_app(app, host=node['host'], port=node['port'])

async def parameters(request):
    return web.json_response(request.app['params'])

async def status(request):
    """get only version of below function"""
    return web.json_response(request.app['node'])


async def status_set(request):
    """
    The status endpoint is used by the orchestrator to inform intent and retrieve
    status of node
        - the module's type
        - the module configuration
        - the module status
    """
    intent = await request.json()
    print('received intent', intent)
    if request.app.get('status_set', None):
        try:
            return await request.app['status_set'](request)
        except:
            pass
    return web.json_response(request.app['node'])

"""
Each server is wrapped by a blade, so launching a module should be done trough
the blade.py
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generic aiohttp server manager")
    parser.add_argument("--node", type=json.loads, default={}, help="JSON string of node configuration")
    parser.add_argument("--topology", type=json.loads, default={}, help="JSON string of topology")
    args = parser.parse_args()

    # Dynamically load the appropriate aiohttp app from the submodule
    mod = __import__(args.node['module'], fromlist=['app'])
    app = getattr(mod, 'app')
    app.router.add_get('/', hello)
    app.router.add_get('/kill', kill)
    app.router.add_get('/parameters', parameters)
    app.router.add_get('/status', status)
    app.router.add_post('/status', status_set)

    asyncio.run(start_blade(args.node, args.topology))

