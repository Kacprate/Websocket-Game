import asyncio
import time
from enum import Enum

import websockets

import modules.logger as logger
import modules.message as message_module

logger = logger.get_logger(__name__)

connected_clients = {}

command_prefix = '/'

class Status(Enum):
    CLOSE = 0,
    SUCCESS = 1,
    ERROR = 2,
    SERVER_SHUTDOWN = 3,
    WARNING = 4

async def handle_leaving(websocket, lost_connection=False):
    client_data = connected_clients[websocket]
    del connected_clients[websocket]

    if lost_connection:
        message = message_module.Message('TEXT', f'{client_data["name"]} lost connection.').pack()
    else:
        message = message_module.Message('TEXT', f'{client_data["name"]} left the server.').pack()

    for client in connected_clients.keys():
        await client.send(message)

async def handle_command(websocket, path, client_data, msg, command, params):
    if command == 'shutdown':
        return Status.SERVER_SHUTDOWN, "Shutting down the server..."

    elif command == 'setname':
        old_name = client_data['name']
        new_name = ' '.join(params)
        client_data['name'] = new_name
        result = f'Setting name of {old_name} to {new_name}.'
        for client in connected_clients.keys():
            await client.send(message_module.Message('TEXT', result).pack())
        return Status.SUCCESS, result

    return Status.WARNING, "Command not recognized."

async def handle_message(websocket, path, client_data, msg):
    if msg.message_type == 'CONNECTION_CLOSE':
        return Status.CLOSE, f'{client_data["name"]} left the server.'

    elif msg.message_type == 'COMMAND':
        msg.data = msg.data[len(command_prefix):]
        parts = msg.data.split(' ')
        command = parts[0]
        params = parts[1:]
        return await handle_command(websocket, path, client_data, msg, command, params)

    elif msg.message_type == "HELLO":
        await websocket.send(message_module.Message('TEXT', 'Welcome to the server!').pack())
        return Status.SUCCESS, f'{client_data["name"]} joined the server.'

    return Status.SUCCESS, None

async def response(websocket, path):
    try:
        if websocket not in connected_clients:
            ip = websocket.remote_address[0]
            port = websocket.remote_address[1]

            client_data = {'join_time': time.time(), 'ip': ip, 'port': port, 'name': f'Unknown{len(connected_clients)}'}
            connected_clients[websocket] = client_data
            logger.info(f'Client connected: {client_data["name"]}')

            while True:
                try:
                    packed_message = await websocket.recv()
                except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK) as e:
                    logger.info(f'Lost connection with {client_data["name"]}')
                    await handle_leaving(websocket, lost_connection=True)
                    break
                except Exception as e:
                    raise e                    

                message = message_module.Message.from_packed(packed_message)
                logger.info(f'Message from {client_data["name"]}, message_type: {message.message_type}, msg: {message.data}')

                try:
                    if message.message_type == "TEXT" and message.data.startswith(command_prefix):
                        message.message_type = "COMMAND"

                    status, result = await handle_message(websocket, path, client_data, message)
                    logger.info(f'MESSAGE_HANDLER: status: {status.name}, result: {result}')
                except Exception as e:
                    logger.error(f'Exception: {e}')
                    status, result = Status.ERROR, None

                if status == Status.CLOSE:
                    logger.info(f'Client {client_data["name"]} closing connection')
                    await handle_leaving(websocket)
                    break
                elif status == Status.ERROR:
                    break
                elif status == Status.SUCCESS:
                    await websocket.send(message_module.Message('STATUS', True).pack())
                    if message.message_type == 'TEXT': # redistributing the message over the connected clients (chat)
                        message.data = client_data['name'] + ': ' + message.data
                        packed_message = message.pack()
                        for client in connected_clients.keys():
                            await client.send(packed_message)
                    elif message.message_type == 'HELLO':
                        for client in connected_clients.keys():
                            await client.send(message_module.Message('TEXT', result).pack())
                elif status == Status.WARNING:
                    # logger.warn(result)
                    pass
                elif status == Status.SERVER_SHUTDOWN:
                    raise NotImplementedError('Shutdown not implemented')

        else:
            logger.warn(f"Client with that IP and port is already connected")
            await websocket.send(message_module.Message('TEXT', "Client with that IP and port is already connected").pack())
    finally:
        if websocket in connected_clients:
            await handle_leaving(websocket)

        await websocket.close()

def run(ip, port):
    start_server = websockets.serve(response, ip, port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
