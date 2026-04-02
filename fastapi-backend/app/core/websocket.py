from fastapi import WebSocket
from typing import List, Dict
import json

class ConnectionManager:
    """Manages WebSocket connections for real-time notifications."""
    def __init__(self):
        # List to store active websocket connections
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new connection and store it."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a connection when it disconnects."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific connection."""
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        """Send a message to all active connections."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # If sending fails, connection might be dead, remove it
                self.active_connections.remove(connection)

# Singleton instance to be used across the app
manager = ConnectionManager()
