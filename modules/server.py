import asyncio
import websockets

async def response(websocket, path):
    try:
        while True:
            message = await websocket.recv()
            print(f"We got the message from the client: {message}")
            await websocket.send(f"Response from server, your message was: {message}")
            if message == 'end':
                break
    finally:
        print('closing')
        await websocket.close()

def run(ip, port):
    start_server = websockets.serve(response, ip, port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()