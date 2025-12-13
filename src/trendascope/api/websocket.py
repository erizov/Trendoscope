"""
WebSocket support for real-time updates.
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connections."""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message, ensure_ascii=False)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_news_update(self, news_item: Dict[str, Any]):
        """Broadcast new news item."""
        await self.broadcast({
            'type': 'news_update',
            'data': news_item,
            'timestamp': datetime.now().isoformat()
        })
    
    async def broadcast_post_update(self, post: Dict[str, Any]):
        """Broadcast post generation update."""
        await self.broadcast({
            'type': 'post_update',
            'data': post,
            'timestamp': datetime.now().isoformat()
        })
    
    async def broadcast_progress(self, task_id: str, progress: int, message: str):
        """Broadcast progress update."""
        await self.broadcast({
            'type': 'progress',
            'task_id': task_id,
            'progress': progress,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    
    Messages sent:
    - news_update: New news item available
    - post_update: Post generation complete
    - progress: Task progress update
    - error: Error occurred
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send_personal_message(
            json.dumps({
                'type': 'connected',
                'message': 'Connected to Trendoscope real-time updates',
                'timestamp': datetime.now().isoformat()
            }),
            websocket
        )
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages (with timeout to allow ping/pong)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                
                # Handle incoming messages (e.g., subscribe to specific channels)
                try:
                    message = json.loads(data)
                    if message.get('type') == 'ping':
                        await manager.send_personal_message(
                            json.dumps({
                                'type': 'pong',
                                'timestamp': datetime.now().isoformat()
                            }),
                            websocket
                        )
                except json.JSONDecodeError:
                    logger.debug(f"Invalid JSON from client: {data}")
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await manager.send_personal_message(
                    json.dumps({
                        'type': 'ping',
                        'timestamp': datetime.now().isoformat()
                    }),
                    websocket
                )
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)

