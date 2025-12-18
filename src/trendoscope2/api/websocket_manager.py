"""
WebSocket manager for real-time updates.
Manages WebSocket connections and broadcasts.
"""
import asyncio
import json
import logging
from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Set[WebSocket] = set()
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, metadata: Dict[str, Any] = None):
        """
        Accept new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            metadata: Optional connection metadata
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        if metadata:
            self.connection_metadata[websocket] = metadata
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove WebSocket connection.
        
        Args:
            websocket: WebSocket connection
        """
        self.active_connections.discard(websocket)
        self.connection_metadata.pop(websocket, None)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """
        Send message to specific connection.
        
        Args:
            message: Message dictionary
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any], exclude: WebSocket = None):
        """
        Broadcast message to all connections.
        
        Args:
            message: Message dictionary
            exclude: Optional WebSocket to exclude from broadcast
        """
        disconnected = []
        
        for connection in self.active_connections:
            if connection == exclude:
                continue
            
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to broadcast to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_news_update(self, news_item: Dict[str, Any]):
        """
        Broadcast news update to all connections.
        
        Args:
            news_item: News item dictionary
        """
        message = {
            "type": "news_update",
            "data": news_item,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(message)
    
    async def broadcast_news_batch(self, news_items: list[Dict[str, Any]]):
        """
        Broadcast batch of news updates.
        
        Args:
            news_items: List of news item dictionaries
        """
        message = {
            "type": "news_batch",
            "data": news_items,
            "count": len(news_items),
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """
        Get number of active connections.
        
        Returns:
            Number of active connections
        """
        return len(self.active_connections)


# Global connection manager
manager = ConnectionManager()
