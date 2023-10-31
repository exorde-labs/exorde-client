#! python3.10

import json
import asyncio
from aiohttp import web, ClientSession
import socket
import ssl

# Variable to store the latest stdin input
latest_stdin = ""
mem = {}


def deep_merge(dict1, dict2):
    """Recursively merge dict2 into dict1."""
    for key, value in dict2.items():
        if key in dict1:
            if isinstance(dict1[key], dict) and isinstance(value, dict):
                deep_merge(dict1[key], value)
            else:
                dict1[key] = value
        else:
            dict1[key] = value
    return dict1


def send_to_logs(data, host="gra1.logs.ovh.com", port=12202):
    # Appending \0 to the end of the data string
    data_with_null_terminator = data + "\0"

    # Establishing a socket connection
    s = socket.create_connection((host, port))

    # Wrapping the socket with SSL/TLS
    ssl_sock = ssl.wrap_socket(s)

    # Sending the data
    ssl_sock.sendall(data_with_null_terminator.encode())

    # Closing the connection
    ssl_sock.close()


import logging


async def read_stdin():
    global latest_stdin, mem
    while True:
        # Blocking call wrapped to be non-blocking
        line = await asyncio.to_thread(input)
        try:
            data = json.loads(line)
            mem = deep_merge(mem, data)
        except:
            pass
        latest_stdin = line

        send_to_logs(line)
        print("sent {}", line)


async def handle_get_stdin(__request__):
    return web.json_response(data=mem)


app = web.Application()
app.router.add_get("/get_stdin", handle_get_stdin)


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    server_task = web._run_app(app, port=10210)
    stdin_task = asyncio.create_task(read_stdin())
    await asyncio.gather(server_task, stdin_task)


if __name__ == "__main__":
    asyncio.run(main())
