import asyncio
import websockets
import argparse
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from websockets.exceptions import ConnectionClosed, InvalidURI

async def interactive_shell(uri):
    """
    Connects to the specified WebSocket URI and provides an interactive shell
    for sending and receiving messages.
    If the connection is lost during sending, it reconnects and resends the message.
    During reconnection, user input is blocked.
    """
    history = InMemoryHistory()
    session = PromptSession(history=history)
    pending_message = None  # Store the message that needs to be resent

    while True:
        try:
            print(f"Attempting to connect to {uri}...")
            async with websockets.connect(uri) as websocket:
                print(f"Connected to {uri}\nType your messages below (Ctrl+D to exit):\n")

                # If there is a pending message, send it
                if pending_message:
                    print(f"Resending pending message: {pending_message}")
                    await websocket.send(pending_message)
                    pending_message = None

                    # Wait for the response from the server
                    try:
                        response = await websocket.recv()
                        print(f"Server: {response}")
                    except ConnectionClosed:
                        print("Connection closed by server.")
                        break

                while True:
                    try:
                        # Read user input with command history support
                        message = await session.prompt_async("You: ")

                        if not message.strip():
                            continue  # Skip empty messages

                        try:
                            # Send the message to the WebSocket server
                            await websocket.send(message)
                        except ConnectionClosed:
                            print("Connection closed while sending message.")
                            pending_message = message  # Store the message to resend
                            break

                        try:
                            # Wait for the response from the server
                            response = await websocket.recv()
                            print(f"Server: {response}")
                        except ConnectionClosed:
                            print("Connection closed by server.")
                            break

                    except (EOFError, KeyboardInterrupt):
                        print("\nExiting...")
                        return

        except ConnectionRefusedError:
            print(f"Could not connect to {uri}. Is the WebSocket server running?")
        except InvalidURI:
            print(f"Invalid WebSocket URI: {uri}")
            return
        except Exception as e:
            print(f"An error occurred: {e}")

        # If connection was lost or failed, enter reconnect mode
        print("Disconnected. Reconnecting in 1 second...")
        await asyncio.sleep(1)


def main():
    parser = argparse.ArgumentParser(description='WebSocket Interactive Shell')
    parser.add_argument('uri', help='WebSocket URI (e.g., ws://localhost:9000)')
    args = parser.parse_args()

    try:
        asyncio.run(interactive_shell(args.uri))
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()

