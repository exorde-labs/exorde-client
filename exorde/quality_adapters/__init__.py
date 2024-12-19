import argparse
import asyncio
from aiohttp import web
import json
import importlib
import logging
import os
import aiohttp
from aiohttp import ClientError
from playwright.async_api import async_playwright
import signal

async def http_handler(request):
    """Handle incoming HTTP POST requests."""
    file_name = request.app['file_name']
    try:
        # Parse the received message
        try:
            data = await request.json()
            logging.debug(f"Raw message received: {data}")
            message_id = data.get("id")
            if not message_id:
                return web.json_response({"error": "Missing message id"}, status=400)
            logging.debug(f"{file_name} parsed message: {data}")
            message = json.loads(data['message'])
        except json.JSONDecodeError as e:
            logging.exception(f"Error decoding JSON in {file_name}")
            return web.json_response({"error": f"Invalid JSON: {e}"}, status=400)
        except Exception as e:
            logging.exception(f"Error processing request in {file_name}")
            return web.json_response({"error": f"Error processing request: {e}"}, status=400)

        # Prepare a response
        try:
            response = await request.app["module"].processing_interface(
                request.app, message
            )
            response = {
                "id": message_id,
                "url": message["url"],
                "response": response
            }
        except Exception as e:
            logging.exception(f"Exception in processing_interface for {file_name}")
            response = {
                "id": message_id,
                "url": message["url"],
                "error": str(e)
            }
        logging.debug(f"{file_name} sent response: {response}")
        return web.json_response(response)

    except Exception as e:
        logging.exception(f"Error in HTTP server for {file_name}")
        return web.json_response({"error": f"Internal server error: {e}"}, status=500)


def dynamic_import(module_name):
    try:
        module = importlib.import_module(module_name)
        return module
    except ImportError as e:
        logging.error(f"Error importing module {module_name}: {e}")
        return None


async def fetch_with_mitigation_factory_playwright(
    max_concurrent_requests=5,
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/116.0.0.0 Safari/537.3"
    ),
):
    semaphore = asyncio.Semaphore(max_concurrent_requests)
    pool_lock = asyncio.Lock()

    # Launch the browser
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True, args=[
        '--no-sandbox',
        '--disable-web-security',  # Disable same-origin policy
        '--disable-features=IsolateOrigins,site-per-process',  # Disable site isolation
        '--disable-site-isolation-trials',  # Disable site isolation trials
        '--disable-dev-shm-usage',
        '--disable-accelerated-video-decode',
    ])
    context = await browser.new_context(user_agent=user_agent)
    pages = [await context.new_page() for _ in range(max_concurrent_requests)]
    page_pool = pages.copy()

    async def fetch_with_mitigation(url):
        await semaphore.acquire()
        async with pool_lock:
            page = page_pool.pop()
        try:
            await page.goto(url, wait_until="domcontentloaded")
            # await asyncio.sleep(5)
        except Exception as e:
            async with pool_lock:
                page_pool.append(page)
            semaphore.release()
            raise e

        async def free():
            async with pool_lock:
                page_pool.append(page)
            semaphore.release()

        return page, free

    async def close_browser(force_close=False):
        print("Closing browser pages...")
        try:
            for page in pages:
                try:
                    await page.close()
                except Exception as e:
                    logging.warning(f"Error closing page: {e}")
            try:
                await browser.close()
            except Exception as e:
                logging.warning(f"Error closing browser {e}")
            if force_close:
                try:
                    pid = browser.process.pid
                    os.kill(pid, signal.SIGKILL)
                    logging.warning(f"Browser process with PID {pid} forcefully killed.")
                except ProcessLookupError:
                    logging.warning(f"Browser process with PID {pid} already terminated.")
                except Exception as e:
                    logging.warning(f"Error forcefully killing browser process: {e}")
            await playwright.stop()
        except Exception as e:
            logging.warning(f"Error during browser closing: {e}")
        finally:
            print("Browser closed.")

    print("Browser initialized")

    return fetch_with_mitigation, close_browser


def fetch_with_mitigation_factory(
    max_concurrent_requests=5,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/116.0.0.0 Safari/537.3"
):
    semaphore = asyncio.Semaphore(max_concurrent_requests)
    session = aiohttp.ClientSession(headers={'User-Agent': user_agent})

    async def fetch_with_mitigation(url, retries=3, delay=2):
        nonlocal session

        async with semaphore:
            for attempt in range(retries):
                try:
                    async with session.get(url, timeout=20) as response:
                        if response.status == 200:
                            return await response.read()
                        else:
                            logging.warning(f"Attempt {attempt + 1}: Received status {response.status}")
                except (ClientError, asyncio.TimeoutError) as e:
                    logging.warning(f"Attempt {attempt + 1}: Error occurred - {e}")

                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                    print(f"Retrying... (attempt {attempt + 2})")
                else:
                    raise e

    return fetch_with_mitigation


def shutdown_signal(loop, close_browser):
    async def shutdown():
        print("Shutdown signal received, killing browser and exiting...")
        try:
            await close_browser(force_close=True)
        except Exception as e:
            logging.warning(f"Failed to close browser forcefully during shutdown: {e}")
        os._exit(0)

    return shutdown


async def start_server(file_name, port):
    app = web.Application()
    app['file_name'] = file_name
    module = dynamic_import(file_name)
    assert module, "There is no such module"
    assert hasattr(module, 'processing_interface'), "Module does not have a `processing_interface` function"
    app['fetch'] = fetch_with_mitigation_factory(max_concurrent_requests=3)
    app['pfetch'], close_browser = await fetch_with_mitigation_factory_playwright(max_concurrent_requests=3)
    app['module'] = module
    app['close_browser'] = close_browser # Store the close_browser function

    app.router.add_post("/", http_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", port)
    print(f"Starting HTTP server for {file_name} on port {port}")
    await site.start()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown_signal(loop, app['close_browser'])()))
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        print("Server shutdown requested.")


def main():
    print("Hello world !")
    parser = argparse.ArgumentParser(
        description="Subprocess HTTP server."
    )
    parser.add_argument(
        "--file_name", required=True, help="Name of the Python script."
    )
    parser.add_argument(
        "--port", required=True, type=int, help="Port for HTTP server."
    )
    args = parser.parse_args()

    log_filename = os.path.splitext(os.path.basename(args.file_name))[0] + '.log'
    logging.basicConfig(
        level=logging.DEBUG,
        filename=log_filename,
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        asyncio.run(start_server(args.file_name, args.port))
    except Exception as e:
        print(e)
        logging.exception(f"Failed to start HTTP server for {args.file_name}")


if __name__ == "__main__":
    main()
