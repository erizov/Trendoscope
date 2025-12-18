"""
Integration tests for WebSocket functionality.
"""
import pytest
import sys
import json
from pathlib import Path
from fastapi.testclient import TestClient

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from trendoscope2.api.main import app


class TestWebSocket:
    """Test WebSocket functionality."""
    
    def test_websocket_connection(self):
        """Test WebSocket connection."""
        client = TestClient(app)
        
        with client.websocket_connect("/api/news/ws") as websocket:
            # Should receive connection message
            data = websocket.receive_json()
            assert data["type"] == "connected"
            assert "message" in data
    
    def test_websocket_ping_pong(self):
        """Test WebSocket ping/pong."""
        client = TestClient(app)
        
        with client.websocket_connect("/api/news/ws") as websocket:
            # Receive connection message
            websocket.receive_json()
            
            # Send ping
            websocket.send_json({"type": "ping"})
            
            # Receive pong
            data = websocket.receive_json()
            assert data["type"] == "pong"
    
    def test_websocket_subscribe(self):
        """Test WebSocket subscription."""
        client = TestClient(app)
        
        with client.websocket_connect("/api/news/ws") as websocket:
            # Receive connection message
            websocket.receive_json()
            
            # Subscribe to channel
            websocket.send_json({
                "type": "subscribe",
                "channel": "news_updates"
            })
            
            # Receive subscription confirmation
            data = websocket.receive_json()
            assert data["type"] == "subscribed"
            assert data["channel"] == "news_updates"
    
    def test_multiple_connections(self):
        """Test multiple WebSocket connections."""
        client = TestClient(app)
        
        with client.websocket_connect("/api/news/ws") as ws1:
            ws1.receive_json()  # Connection message
            
            with client.websocket_connect("/api/news/ws") as ws2:
                ws2.receive_json()  # Connection message
                
                # Both should be connected
                data1 = ws1.receive_json()
                # Connection count should be updated
                assert "connections" in data1 or data1.get("type") == "connected"
