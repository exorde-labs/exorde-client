from aiohttp import web
import logging
import asyncio
import os
from typing import Callable
from exorde.persist import PersistedDict
import ssl
import os


def deep_merge(original_context: dict, update_context: dict) -> dict:
    for key, value in update_context.items():
        if (
            key in original_context
            and isinstance(original_context[key], dict)
            and isinstance(value, dict)
        ):
            deep_merge(original_context[key], value)
        else:
            original_context[key] = value
    return original_context


def websocket_handler_factory():
    to_send = []  # Create a local list within the closure
    connected_clients = set()  # Keep track of connected clients
    merged: PersistedDict = PersistedDict("/tmp/exorde/slog.json")
    # merged: dict = {}

    async def websocket_handler(request):
        nonlocal to_send  # Access the local list from the closure
        nonlocal merged

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        try:
            # Send all messages to the new user when they connect
            # for message in to_send:
            #    await ws.send_str(message)
            await ws.send_json(dict(merged))

            # Add the client to the set of connected clients
            connected_clients.add(ws)

            while True:
                # Sleep briefly to allow handling other tasks
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            pass
        finally:
            # Remove the client from the set of connected clients
            connected_clients.remove(ws)
            await ws.close()
        return

    async def ws_push(message):
        nonlocal to_send  # Access the local list from the closure
        nonlocal merged
        logging.info(f"WS_PUSH:'{message}'")
        if isinstance(message, str):
            raise TypeError(f"Accept only dict ({message})")
        else:
            await merged.deep_merge(message)
            # merged = deep_merge(merged, message)
            # to_send.append(json.dumps(message))

        # Send the new message to all connected clients
        for client in connected_clients:
            try:
                await client.send_json(message)
            except Exception:
                pass

    return (
        websocket_handler,
        ws_push,
    )


async def index_handler(request):
    with open("./ui/dist/index.html", "r") as file:
        html_content = file.read()
    return web.Response(text=html_content, content_type="text/html")


import argparse


async def setup_web(command_line_arguments: argparse.Namespace) -> Callable:
    if command_line_arguments.web:
        # Create an aiohttp application
        app = web.Application()

        # Get both the WebSocket handler and the push function from the factory
        websocket_handler, ws_push = websocket_handler_factory()

        # Add a WebSocket route, using the handler from the factory
        app.router.add_get("/ws", websocket_handler)
        dist_folder = os.path.abspath("./ui/dist")
        logging.info(f"serving static from {dist_folder}")
        app.router.add_get("/", index_handler)
        app.router.add_static("/", dist_folder)

        # Load SSL/TLS context with the generated certificate and private key
        CERT_PATH = os.getenv("CERT_PATH")
        if CERT_PATH:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(
                CERT_PATH, keyfile=os.getenv("CERT_KEYFILE")
            )
            PORT = 443
        else:
            ssl_context = None
            PORT = 8080
        # Combine the WebSocket app with the existing app
        runner = web.AppRunner(app)
        await runner.setup()

        # Start the server
        site = web.TCPSite(runner, "0.0.0.0", PORT, ssl_context=ssl_context)
        await site.start()

        logging.info("")
        logging.info("")
        logging.info("")
        logging.info(f"serving on {PORT} (ssl_context={ssl_context})")
        logging.info("")
        logging.info("")
        logging.info("")

        # Return the ws_push function
        return ws_push

    async def do_nothing(message):
        pass

    return do_nothing
