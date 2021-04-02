import asyncio
from threading import Thread

import websocket

import modules.logger as logger
import modules.message as message_module

logger = logger.get_logger(__name__)
connected = False

def send_message(websocket, msg):
    # msg = input("Message: ")
    if msg == '':
        return

    if msg == '/end':
        message = message_module.Message('CONNECTION_CLOSE', msg)
    elif msg.startswith('/setname'):
        message = message_module.Message('TEXT', msg)
    else:
        message = message_module.Message('TEXT', msg)

    websocket.send(message.pack())

    if message.message_type == 'CONNECTION_CLOSE':
        print('Connection closed, press enter to continue.')
        websocket.close()
        return

def on_message(websocket, packed_response):
    if packed_response is None:
        return

    response = message_module.Message.from_packed(packed_response)

    if response.message_type == 'TEXT':
        logger.info(response.data)
    elif response.message_type == 'STATUS':
        logger.info(response.data)

def on_open(websocket):
    global connected
    connected = True
    websocket.send(message_module.Message('HELLO', "").pack())

def on_error(websocket, error_msg):
    logger.error(error_msg)

def on_close(websocket):
    global connected
    connected = False
    raise Exception('websocket closed, do something')

def game_thread(app):
    while True:
        message = input()
        
        if not connected:
            break

        try:
            send_message(app, message)
        except websocket._exceptions.WebSocketConnectionClosedException as e:
            logger.info('Connection is closed')
            break
        except Exception as e:
            raise e

def run(ip, port):
    websocket_url = f'ws://{ip}:{port}'
    app = websocket.WebSocketApp(websocket_url, 
                                 on_message=on_message,
                                 on_error=on_error,
                                 on_close=on_close,
                                 on_open=on_open)

    thread = Thread(target=app.run_forever)
    thread.start()

    game_thread(app)
