import asyncio
import time
from enum import Enum

import websockets

import modules.logger as logger
import modules.message as message_module

logger = logger.get_logger(__name__)

connected_clients = {}

class Status(Enum):
    CLOSE = 0,
    SUCCESS = 1,
    ERROR = 2


def handle_message(websocket, path, client_data, msg):
    if msg.message_type == 'CONNECTION_CLOSE':
        return Status.CLOSE, None
    elif msg.message_type == 'SET_NAME':
        old_name = client_data['name']
        new_name = msg.data
        client_data['name'] = new_name
        return Status.SUCCESS, f'Setting name of {old_name} to {new_name}'

    return Status.SUCCESS, None

async def response(websocket, path):
    try:
        if websocket not in connected_clients:
            ip = websocket.remote_address[0]
            port = websocket.remote_address[1]

            client_data = {'join_time': time.time(), 'ip': ip, 'port': port, 'name': f'ip: {ip}, port: {port}'}
            connected_clients[websocket] = client_data
            print(f'Client connected: {client_data["name"]}')

            while True:
                packed_message = await websocket.recv()
                message = message_module.Message.from_packed(packed_message)
                print(f'Message from {client_data["name"]}: {message.data}')

                try:
                    status, result = handle_message(websocket, path, client_data, message)
                    if result:
                        logger.info(result)
                except Exception as e:
                    print(f'Exception: {e}')
                    status, result = Status.ERROR, None

                if status == Status.CLOSE:
                    logger.info(f'Client {client_data["name"]} closing connection')
                    break
                elif status == Status.ERROR:
                    break
                elif status == Status.SUCCESS:
                    await websocket.send(message_module.Message('STATUS', True).pack())

        else:
            logger.warn(f"Client with that IP and port is already connected")
            await websocket.send(message_module.Message('TEXT', "Client with that IP and port is already connected").pack())

    finally:
        if websocket in connected_clients:
            del connected_clients[websocket]

        await websocket.close()

def run(ip, port):
    start_server = websockets.serve(response, ip, port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
