from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from datetime import datetime
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/queue")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now
            await websocket.send_text(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Call this function whenever queue status changes
async def notify_queue_update(queue_entry_id: int, update_type: str):
    message = {
        "type": update_type,
        "queue_entry_id": queue_entry_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast(message)
