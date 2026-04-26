from fastapi import WebSocket
from typing import Dict, Any

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, run_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[run_id] = websocket

    def disconnect(self, run_id: str):
        if run_id in self.active_connections:
            del self.active_connections[run_id]

    async def send_personal_message(self, message: str, run_id: str):
        if run_id in self.active_connections:
            websocket = self.active_connections[run_id]
            try:
                await websocket.send_text(message)
            except Exception:
                pass

    async def send_json(self, data: dict, run_id: str):
        if run_id in self.active_connections:
            websocket = self.active_connections[run_id]
            try:
                await websocket.send_json(data)
            except Exception:
                pass

manager = ConnectionManager()
