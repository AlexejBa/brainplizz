import asyncio
import json

import websockets


ROOM_ID = "ec46ce16-2be1-4c3e-ba2c-1192f10abf57"
USER_ID = "a0005b70-4121-442b-aa60-0b1b825caf4e"


async def test_websocket():
    uri = (
        f"ws://127.0.0.1:8000/ws/rooms/"
        f"{ROOM_ID}?user_id={USER_ID}"
    )

    async with websockets.connect(uri) as websocket:

        print("WebSocket подключен")

        while True:
            message = await websocket.recv()

            print("Сервер:", message)


asyncio.run(test_websocket())