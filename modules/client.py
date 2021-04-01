import asyncio
import websockets

async def message(websocket_url):
    async with websockets.connect(websocket_url) as socket:
        while True:
            msg = input("Message: ")
            await socket.send(msg)
            print(await socket.recv())
            if msg == 'end':
                break

def run(ip, port):
    websocket_url = f'ws://{ip}:{port}'
    asyncio.get_event_loop().run_until_complete(message(websocket_url=websocket_url))
