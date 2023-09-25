from aiohttp import web
import logging
import asyncio
import os
from typing import Callable
import json


def websocket_handler_factory():
    to_send = []  # Create a local list within the closure
    connected_clients = set()  # Keep track of connected clients

    async def websocket_handler(request):
        nonlocal to_send  # Access the local list from the closure

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        try:
            # Send all messages to the new user when they connect
            for message in to_send:
                await ws.send_str(message)

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
        if isinstance(message, str):
            to_send.append(message)
        else:
            to_send.append(json.dumps(message))

        # Send the new message to all connected clients
        for client in connected_clients:
            try:
                if isinstance(message, str):
                    await client.send_str(message)
                else:
                    await client.send_str(json.dumps(message))
            except:
                pass

    return (
        websocket_handler,
        ws_push,
    )


async def index_handler(request):
    with open("./ui/dist/index.html", "r") as file:
        html_content = file.read()
    return web.Response(text=html_content, content_type="text/html")


async def setup_web() -> Callable:
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

    # Combine the WebSocket app with the existing app
    runner = web.AppRunner(app)
    await runner.setup()

    # Start the server
    site = web.TCPSite(runner, "localhost", 8080)
    await site.start()

    logging.info("serving on 8080")

    # Return the ws_push function
    return ws_push


if __name__ == "__main__":
    ws_push_function = asyncio.get_event_loop().run_until_complete(setup_web())
    asyncio.get_event_loop().run_forever()
