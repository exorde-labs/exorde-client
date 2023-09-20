from aiohttp import web
import logging
import asyncio
import os


# WebSocket handler closure
def websocket_handler_factory():
    to_send = []  # Create a local list within the closure

    async def websocket_handler(request):
        nonlocal to_send  # Access the local list from the closure

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        try:
            while True:
                if to_send:
                    message = to_send.pop(
                        0
                    )  # Get the oldest message from the local list
                    await ws.send_str(message)
                else:
                    await asyncio.sleep(
                        1
                    )  # Sleep if there are no messages to send
        except asyncio.CancelledError:
            pass
        finally:
            await ws.close()

    async def ws_push(message):
        nonlocal to_send  # Access the local list from the closure
        to_send.append(message)

    return (
        websocket_handler,
        ws_push,
    )  # Return both the handler and the push function


async def index_handler(request):
    with open("./ui/dist/index.html", "r") as file:
        html_content = file.read()
    return web.Response(text=html_content, content_type="text/html")


async def setup_web():
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
