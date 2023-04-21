import json, asyncio, subprocess, time
from aiohttp import ClientSession
from aiosow.bindings import alias, setup
from aiosow.autofill import autofill


@setup
async def launch_browser():
    subprocess.Popen(
        [
            "/home/patrick/.cache/ms-playwright/chromium-1048/chrome-linux/chrome",
            "--remote-debugging-port=9222",
        ]
    )
    await asyncio.sleep(0.5)


@alias("page_websocket_url")
async def get_page_websocket_url():
    async with ClientSession() as session:
        async with session.get("http://localhost:9222/json/list") as response:
            tabs = await response.json()
            tab_info = tabs[0]
            return tab_info["webSocketDebuggerUrl"]


@setup
async def create_websocket_client(page_websocket_url):
    websocket_session = ClientSession()
    websocket = await websocket_session.ws_connect(page_websocket_url)
    return {"page_websocket_session": websocket_session, "page_websocket": websocket}


async def send_command(command: dict, page_websocket):
    await page_websocket.send_str(json.dumps(command))


@setup
async def enable_network(page_websocket):
    await send_command(
        {"id": 1, "method": "Network.enable", "params": {}}, page_websocket
    )


async def goto(url: str, page_websocket):
    await send_command(
        {
            "id": 2,
            "method": "Page.navigate",
            "params": {"url": url},
        },
        page_websocket,
    )


async def evaluate_expression(expression: str, page_websocket):
    await send_command(
        {
            "id": 3,
            "method": "Runtime.evaluate",
            "params": {"expression": expression},
        },
        page_websocket,
    )


handlers = {}
interceptions = {}


def intercept(url: str):
    def decorator(func):
        interceptions[url] = func
        return func

    return decorator


def add_handler(filter_dict, func):
    filter_keys = tuple(filter_dict.items())
    handlers[filter_keys] = func


def remove_handler(filter_dict):
    filter_keys = tuple(filter_dict.items())
    if filter_keys in handlers:
        del handlers[filter_keys]


def handler(filter_dict):
    def decorator(func):
        add_handler(filter_dict, func)
        return func

    return decorator


def interception_handler(function):
    async def do_intercept(message, __page_websocket__, memory):
        await autofill(
            function,
            args=[
                message,
            ],
            memory=memory,
        )
        return (remove_handler, ({"id": message["id"]},))

    return do_intercept


def generate_request_id():
    return int(time.time())


@handler({"method": "Network.responseReceived"})
async def network_response_received(message, page_websocket, __memory__):
    if not message["params"]["response"]["url"].startswith("data:"):
        url = message["params"]["response"]["url"]
        request_id = message["params"]["requestId"]
        for interception, function in interceptions.items():
            if interception in url or interception == url:
                transaction_id = generate_request_id()
                await send_command(
                    {
                        "id": transaction_id,
                        "method": "Network.getResponseBody",
                        "params": {"requestId": request_id},
                    },
                    page_websocket,
                )
                return (
                    add_handler,
                    ({"id": transaction_id}, interception_handler(function)),
                )


async def handle_message(message, page_websocket, memory):
    message_data = json.loads(message)  # / ! \ everything is json loaded
    updates = []
    for filter_keys, handler_func in handlers.items():
        if all(k in message_data and message_data[k] == v for k, v in filter_keys):
            update = await handler_func(message_data, page_websocket, memory)
            if update:
                updates.append(update)
    for update in updates:
        update[0](*update[1])


async def listen_page_websocket(page_websocket, memory):
    async for message in page_websocket:  # appropriatly an infinite loop
        await handle_message(message.data, page_websocket, memory)


@setup
async def run_websocket_client(memory):
    return autofill(listen_page_websocket, args=[], memory=memory)
