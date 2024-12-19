import asyncio
import aiohttp
import json
from pathlib import Path
import uuid
import subprocess
import logging
import os
from collections import Counter
import signal

def print_all_tasks():
    """
    Print all tasks currently in the asyncio event loop grouped by coroutine name with counts.
    """
    current_tasks = asyncio.all_tasks()  # Get all tasks in the current event loop
    print(f"Found {len(current_tasks)} task(s) in the event loop:")

    # Group tasks by coroutine name
    coro_names = []
    for task in current_tasks:
        coro = task.get_coro()
        coro_name = getattr(coro, "__name__", str(coro))
        coro_names.append(coro_name)

    # Count and display grouped coroutine names with counts
    coro_counter = Counter(coro_names)
    for coro_name, count in coro_counter.items():
        print(f"- {coro_name} (x{count})")


class ProcessManager:
    def __init__(self, folder_path):
        self.folder_path = Path(folder_path)
        if not self.folder_path.exists() or not self.folder_path.is_dir():
            raise ValueError(f"Invalid folder path: {folder_path}")

        self.process_pool = {}
        self.ports = {}
        self.next_port = 8000  # Start assigning ports from 8000
        self.message_futures = {}  # {file_name: {message_id: Future}}
        self.logger_tasks = {}
        self.server_back_online_event = {}
        self.client_sessions = {}
        self.request_timeout = 30  # Timeout for HTTP requests in seconds
        self.shutdown_wait_time = 5  # Time to wait for subprocesses to terminate in seconds

    async def wait_for_event_server_back_online(self, file_name: str):
        """
        `wait_for_event_server_back_online` is used on server restart by the
        `quality_report.py` on task_cancelation in order to wait for the server
        to be back online. Once it is done it can respawn the cancelled tasks.
        """
        await self.server_back_online_event[file_name].wait()

    async def _restart_subprocess(self, file_name):
        print_all_tasks()
        logging.info(f"Restarting subprocess {file_name}...")

        self.server_back_online_event[file_name] = asyncio.Event()

        if file_name in self.logger_tasks:
            logger_task = self.logger_tasks.pop(file_name)
            logger_task.cancel()
            try:
                await asyncio.gather(logger_task)
            except asyncio.CancelledError:
                logging.info(f"Logger task for {file_name} cancelled.")

        logging.info(f"Terminating subprocess {file_name}...")
        self.kill_pending_futures(file_name)

        if file_name in self.process_pool:
            process = self.process_pool.pop(file_name)
            process.terminate()
            process.wait()
            logging.info(f"Subprocess {file_name} terminated.")

        if file_name in self.client_sessions:
            session = self.client_sessions.pop(file_name)
            await session.close()
            logging.info(f"Client session for {file_name} closed.")

        logging.info(f"Restarting subprocess {file_name}...")
        port = self.ports[file_name]
        self._start_subprocess(file_name, port)
        await asyncio.sleep(0.5)
        await self._create_client_session(file_name)
        logging.info(f"Subprocess {file_name} started !")

        self.server_back_online_event[file_name].set()

    def start_subprocesses(self):
        """Start all Python subprocesses in the folder."""
        for script in self.folder_path.glob("*.py"):
            if script.name == "__init__.py":
                continue
            file_name = script.stem
            port = self.next_port
            self.next_port += 1  # Increment the port for the next subprocess

            self._start_subprocess(file_name, port)

    def _start_subprocess(self, file_name, port):
        """Start a single subprocess."""
        # the -u option stands for `unbuffered` and allows immediate communication
        # trough pipes
        process = subprocess.Popen(
            ["python", "-u", str(self.folder_path / "__init__.py"), "--file_name", file_name, "--port", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.process_pool[file_name] = process
        self.ports[file_name] = port
        logging.info(f"Started {file_name} on port {port}")

        self.logger_tasks[file_name] = asyncio.create_task(self._log_subprocess_output(file_name, process))

    def kill_pending_futures(self, file_name):
        """
        Cancel and remove all pending futures for the specified file_name.
        """
        if file_name not in self.message_futures:
            logging.info(f"No pending futures to kill for {file_name}.")
            return

        logging.info(f"Killing all pending futures for {file_name}...")
        futures = self.message_futures.pop(file_name)

        for message_id, future in futures.items():
            if not future.done():
                future.cancel()
                logging.debug(f"Cancelled future for message_id {message_id}.")

    async def _log_subprocess_output(self, file_name, process):
        """Asynchronously log stdout and stderr of a subprocess."""
        try:
            async def _log_stream(stream, prefix):
                while True:
                    await asyncio.sleep(.1)
                    if not stream:
                        break
                    try:
                        # Attempt to read a line with a timeout
                        line_task = asyncio.create_task(asyncio.to_thread(stream.readline))
                        try:
                          line = await asyncio.wait_for(line_task, timeout=0.1)
                        except asyncio.TimeoutError:
                            line_task.cancel()
                            break
                        if not line:
                          break
                        logging.info(f"[{file_name} {prefix}] {line.strip()}")

                    except Exception as e:
                        logging.error(f"Error reading from stream for {file_name} ({prefix}): {e}")
                        break
            await asyncio.gather(
                _log_stream(process.stdout, "STDOUT"),
                _log_stream(process.stderr, "STDERR"),
            )
        except Exception as e:
            logging.error(f"Failed to log output for {file_name}: {e}")

    async def _check_servers_ready(self):
        """Check if all servers are ready by attempting a socket connection."""
        tasks = []
        for file_name, port in self.ports.items():
            tasks.append(self._wait_for_server(file_name, "localhost", port))
        await asyncio.gather(*tasks)

    async def _wait_for_server(self, file_name, host, port, timeout=30000):
        """Wait until the server at (host, port) is accepting connections."""
        start_time = asyncio.get_event_loop().time()
        while True:
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"Server on {host}:{port} not ready after {timeout} seconds.")

            proc = self.process_pool[file_name]
            if proc.poll() is not None:
                logging.error(f"Subprocess {file_name} exited unexpectedly.")
                raise RuntimeError(f"Subprocess {file_name} exited unexpectedly.")

            try:
                reader, writer = await asyncio.open_connection(host, port)
                writer.close()
                await writer.wait_closed()
                logging.info(f"Server ready on {host}:{port}")
                return
            except (ConnectionRefusedError, OSError):
                await asyncio.sleep(0.1)

    async def connect_to_subprocesses(self):
        """Connect to all subprocess HTTP servers and start receiver tasks."""
        for file_name, port in self.ports.items():
            await self._create_client_session(file_name)

    async def _create_client_session(self, file_name):
        """Create a client session for a single subprocess."""
        try:
            session = aiohttp.ClientSession()
            self.client_sessions[file_name] = session
            self.message_futures[file_name] = {}
            logging.info(f"Client session created for {file_name}.")
        except Exception as e:
            logging.error(f"Failed to create client session for {file_name}: {e}")
            await asyncio.sleep(1)
            await self._restart_subprocess(file_name)

    async def send(self, file_name, message):
        """Send a message to a subprocess and await its response."""
        if file_name not in self.client_sessions:
            raise ValueError(f"No client session for {file_name}")

        session = self.client_sessions[file_name]
        port = self.ports[file_name]
        url = f"http://localhost:{port}/"
        message_id = str(uuid.uuid4())
        request = {"id": message_id, "message": message}

        try:
            logging.debug(f"Sending to {file_name}: {request}")
            async with session.post(url, json=request, timeout=self.request_timeout) as response:
                response.raise_for_status()
                data = await response.json()
                logging.debug(f"Received from {file_name}: {data}")
                return data
        except aiohttp.ClientError as e:
            logging.error(f"Error sending request to {file_name} at {url}: {e}")
            await self._restart_subprocess(file_name)
            return None
        except asyncio.TimeoutError:
            logging.error(f"Timeout waiting for response from {file_name} for message_id {message_id}")
            await self._restart_subprocess(file_name)
            return None
        except Exception as e:
            logging.exception(f"Error waiting for response from {file_name} for message_id {message_id}: {e}")
            return None
        finally:
            print_all_tasks()

    async def __aenter__(self):
        """Start subprocesses, check servers, and connect to them."""
        self.start_subprocesses()
        await self._check_servers_ready()
        await self.connect_to_subprocesses()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Clean up connections and terminate subprocesses."""
        # Close all client sessions
        for session in list(self.client_sessions.values()):
            await session.close()
        self.client_sessions.clear()

        # Terminate all subprocesses
        for file_name, process in list(self.process_pool.items()):  # Use a static copy
            try:
                logging.info(f"Sending SIGTERM to subprocess {file_name} with PID {process.pid}")
                process.send_signal(signal.SIGTERM)
            except ProcessLookupError:
                logging.warning(f"Subprocess {file_name} with PID {process.pid} already terminated.")
            except Exception as e:
                logging.warning(f"Error sending SIGTERM to subprocess {file_name}: {e}")

        await asyncio.sleep(self.shutdown_wait_time)

        for file_name, process in list(self.process_pool.items()):
            try:
                pid = process.pid
                process.stdout.close()
                process.stderr.close()
                os.kill(pid, signal.SIGKILL)
                logging.warning(f"Subprocess {file_name} with PID {pid} forcefully killed.")
            except ProcessLookupError:
                logging.warning(f"Subprocess {file_name} with PID {pid} already terminated.")
            except Exception as e:
                logging.warning(f"Error forcefully killing subprocess {file_name}: {e}")
        self.process_pool.clear()
        # Clear message futures
        self.message_futures.clear()
        print("Cleaned up all subprocesses and connections.")
