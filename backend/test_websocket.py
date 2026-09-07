import asyncio
import json

import websockets


ROOM_ID = "fd15c276-881d-45c5-8ba8-319a242e137f"
USER_ID = "a0005b70-4121-442b-aa60-0b1b825caf4e"


async def test_websocket():
    uri = (
        f"ws://127.0.0.1:8000/ws/rooms/"
        f"{ROOM_ID}?user_id={USER_ID}"
    )

    async with websockets.connect(uri) as websocket:

        message = await websocket.recv()

        print("Сервер:", message)

        await websocket.send(
            json.dumps({
                "type": "test",
                "message": "Привет, BrainPlizz!"
            })
        )

        response = await websocket.recv()

        print("Сервер:", response)


asyncio.run(test_websocket())