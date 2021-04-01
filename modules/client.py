import asyncio

import websockets

import modules.logger as logger
import modules.message as message_module

logger = logger.get_logger(__name__)

async def message(websocket_url):
    async with websockets.connect(websocket_url) as socket:
        while True:
            msg = input("Message: ")

            if msg == '/end':
                message = message_module.Message('CONNECTION_CLOSE', msg)
            elif msg.startswith('/setname'):
                data = msg.split(' ')
                name = ' '.join(data[1:])
                message = message_module.Message('SET_NAME', name)
            else:
                message = message_module.Message('TEXT', msg)

            await socket.send(message.pack())

            if message.message_type == 'CONNECTION_CLOSE':
                break

            packed_response = await socket.recv()
            response = message_module.Message.from_packed(packed_response)

            if response.message_type == 'TEXT':
                print(response.data)
            elif response.message_type == 'STATUS':
                print(response.data)
            

def run(ip, port):
    websocket_url = f'ws://{ip}:{port}'
    asyncio.get_event_loop().run_until_complete(message(websocket_url=websocket_url))
