from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.rooms: dict[UUID, dict[UUID, WebSocket]] = {}

    async def connect(
        self,
        room_id: UUID,
        user_id: UUID,
        websocket: WebSocket
    ):
        await websocket.accept()

        if room_id not in self.rooms:
            self.rooms[room_id] = {}

        self.rooms[room_id][user_id] = websocket

    def disconnect(
        self,
        room_id: UUID,
        user_id: UUID
    ):
        if room_id not in self.rooms:
            return

        self.rooms[room_id].pop(user_id, None)

        if not self.rooms[room_id]:
            del self.rooms[room_id]

    async def send_to_user(
        self,
        room_id: UUID,
        user_id: UUID,
        message: dict
    ):
        websocket = self.rooms.get(room_id, {}).get(user_id)

        if websocket:
            await websocket.send_json(message)

    async def broadcast(
        self,
        room_id: UUID,
        message: dict
    ):
        connections = self.rooms.get(room_id, {})

        for websocket in connections.values():
            await websocket.send_json(message)