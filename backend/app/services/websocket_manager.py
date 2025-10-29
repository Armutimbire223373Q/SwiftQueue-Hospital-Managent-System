"""
Enhanced WebSocket Manager for real-time features.
Provides connection management, presence tracking, room-based messaging, and event broadcasting.
"""

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, Set, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class ConnectionInfo:
    """Information about a WebSocket connection"""
    
    def __init__(
        self,
        websocket: WebSocket,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        role: Optional[str] = None,
        connection_type: str = "general"
    ):
        self.websocket = websocket
        self.user_id = user_id
        self.username = username
        self.role = role
        self.connection_type = connection_type
        self.connected_at = datetime.utcnow()
        self.last_ping = datetime.utcnow()
        self.rooms: Set[str] = set()
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert connection info to dictionary"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role,
            "connection_type": self.connection_type,
            "connected_at": self.connected_at.isoformat(),
            "connected_duration": (datetime.utcnow() - self.connected_at).total_seconds(),
            "rooms": list(self.rooms),
            "metadata": self.metadata
        }


class EnhancedWebSocketManager:
    """
    Enhanced WebSocket connection manager with:
    - User presence tracking
    - Room-based messaging
    - Event broadcasting
    - Connection pooling
    - Heartbeat monitoring
    """
    
    def __init__(self):
        # Connection storage
        self.connections: Dict[str, ConnectionInfo] = {}  # connection_id -> ConnectionInfo
        self.user_connections: Dict[int, Set[str]] = defaultdict(set)  # user_id -> set of connection_ids
        self.room_connections: Dict[str, Set[str]] = defaultdict(set)  # room_name -> set of connection_ids
        
        # Legacy support
        self.active_connections: List[WebSocket] = []
        self.dashboard_connections: List[WebSocket] = []
        self.patient_connections: Dict[str, WebSocket] = {}
        
        # Statistics
        self.total_connections = 0
        self.total_messages_sent = 0
        self.total_messages_received = 0
        
        # Heartbeat configuration
        self.heartbeat_interval = 30  # seconds
        self.connection_timeout = 120  # seconds
        
        logger.info("Enhanced WebSocket Manager initialized")
    
    def generate_connection_id(self) -> str:
        """Generate unique connection ID"""
        self.total_connections += 1
        return f"conn_{self.total_connections}_{datetime.utcnow().timestamp()}"
    
    async def connect(
        self,
        websocket: WebSocket,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        role: Optional[str] = None,
        connection_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Connect a WebSocket with enhanced tracking.
        
        Returns:
            connection_id: Unique identifier for this connection
        """
        await websocket.accept()
        
        connection_id = self.generate_connection_id()
        conn_info = ConnectionInfo(
            websocket=websocket,
            user_id=user_id,
            username=username,
            role=role,
            connection_type=connection_type
        )
        
        if metadata:
            conn_info.metadata.update(metadata)
        
        # Store connection
        self.connections[connection_id] = conn_info
        
        # Track user connections
        if user_id:
            self.user_connections[user_id].add(connection_id)
        
        # Legacy support
        if connection_type == "dashboard":
            self.dashboard_connections.append(websocket)
        else:
            self.active_connections.append(websocket)
        
        logger.info(
            f"WebSocket connected: {connection_id} "
            f"(user_id={user_id}, username={username}, type={connection_type})"
        )
        
        # Send connection confirmation
        await self.send_to_connection(connection_id, {
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "username": username
        })
        
        # Broadcast presence update
        if user_id and username:
            await self.broadcast_presence_update(user_id, username, "online")
        
        return connection_id
    
    def disconnect(
        self,
        connection_id: str,
        notify_presence: bool = True
    ):
        """Disconnect a WebSocket connection"""
        if connection_id not in self.connections:
            return
        
        conn_info = self.connections[connection_id]
        
        # Remove from rooms
        for room in list(conn_info.rooms):
            self.leave_room(connection_id, room)
        
        # Remove from user connections
        if conn_info.user_id:
            self.user_connections[conn_info.user_id].discard(connection_id)
            if not self.user_connections[conn_info.user_id]:
                del self.user_connections[conn_info.user_id]
        
        # Legacy support
        if conn_info.websocket in self.dashboard_connections:
            self.dashboard_connections.remove(conn_info.websocket)
        if conn_info.websocket in self.active_connections:
            self.active_connections.remove(conn_info.websocket)
        
        # Remove connection
        del self.connections[connection_id]
        
        logger.info(f"WebSocket disconnected: {connection_id}")
        
        # Broadcast presence update
        if notify_presence and conn_info.user_id and conn_info.username:
            asyncio.create_task(
                self.broadcast_presence_update(
                    conn_info.user_id,
                    conn_info.username,
                    "offline"
                )
            )
    
    async def send_to_connection(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ) -> bool:
        """
        Send message to a specific connection.
        
        Returns:
            bool: True if message sent successfully
        """
        if connection_id not in self.connections:
            return False
        
        conn_info = self.connections[connection_id]
        
        try:
            message_str = json.dumps(message)
            await conn_info.websocket.send_text(message_str)
            self.total_messages_sent += 1
            return True
        except Exception as e:
            logger.error(f"Error sending to {connection_id}: {e}")
            self.disconnect(connection_id)
            return False
    
    async def send_to_user(
        self,
        user_id: int,
        message: Dict[str, Any]
    ) -> int:
        """
        Send message to all connections of a specific user.
        
        Returns:
            int: Number of connections message was sent to
        """
        if user_id not in self.user_connections:
            return 0
        
        connection_ids = list(self.user_connections[user_id])
        sent_count = 0
        
        for conn_id in connection_ids:
            if await self.send_to_connection(conn_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast(
        self,
        message: Dict[str, Any],
        exclude_connections: Optional[Set[str]] = None,
        filter_by_role: Optional[List[str]] = None,
        filter_by_type: Optional[str] = None
    ) -> int:
        """
        Broadcast message to all connections with optional filters.
        
        Returns:
            int: Number of connections message was sent to
        """
        exclude_connections = exclude_connections or set()
        sent_count = 0
        
        for conn_id, conn_info in list(self.connections.items()):
            if conn_id in exclude_connections:
                continue
            
            if filter_by_role and conn_info.role not in filter_by_role:
                continue
            
            if filter_by_type and conn_info.connection_type != filter_by_type:
                continue
            
            if await self.send_to_connection(conn_id, message):
                sent_count += 1
        
        return sent_count
    
    def join_room(self, connection_id: str, room_name: str):
        """Add connection to a room"""
        if connection_id not in self.connections:
            return
        
        self.connections[connection_id].rooms.add(room_name)
        self.room_connections[room_name].add(connection_id)
        
        logger.info(f"Connection {connection_id} joined room: {room_name}")
    
    def leave_room(self, connection_id: str, room_name: str):
        """Remove connection from a room"""
        if connection_id not in self.connections:
            return
        
        self.connections[connection_id].rooms.discard(room_name)
        self.room_connections[room_name].discard(connection_id)
        
        if not self.room_connections[room_name]:
            del self.room_connections[room_name]
        
        logger.info(f"Connection {connection_id} left room: {room_name}")
    
    async def broadcast_to_room(
        self,
        room_name: str,
        message: Dict[str, Any],
        exclude_connections: Optional[Set[str]] = None
    ) -> int:
        """
        Broadcast message to all connections in a room.
        
        Returns:
            int: Number of connections message was sent to
        """
        if room_name not in self.room_connections:
            return 0
        
        exclude_connections = exclude_connections or set()
        connection_ids = list(self.room_connections[room_name])
        sent_count = 0
        
        for conn_id in connection_ids:
            if conn_id not in exclude_connections:
                if await self.send_to_connection(conn_id, message):
                    sent_count += 1
        
        return sent_count
    
    async def broadcast_presence_update(
        self,
        user_id: int,
        username: str,
        status: str
    ):
        """Broadcast user presence update to all connections"""
        message = {
            "type": "presence_update",
            "user_id": user_id,
            "username": username,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast(message)
        logger.info(f"Presence update: {username} is {status}")
    
    def get_online_users(self) -> List[Dict[str, Any]]:
        """Get list of online users"""
        online_users = {}
        
        for user_id, connection_ids in self.user_connections.items():
            if connection_ids:
                # Get first connection's info
                first_conn_id = next(iter(connection_ids))
                if first_conn_id in self.connections:
                    conn_info = self.connections[first_conn_id]
                    online_users[user_id] = {
                        "user_id": user_id,
                        "username": conn_info.username,
                        "role": conn_info.role,
                        "connection_count": len(connection_ids),
                        "connected_at": conn_info.connected_at.isoformat()
                    }
        
        return list(online_users.values())
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.connections),
            "total_users": len(self.user_connections),
            "total_rooms": len(self.room_connections),
            "total_messages_sent": self.total_messages_sent,
            "total_messages_received": self.total_messages_received,
            "connections_by_type": {
                conn_type: sum(
                    1 for c in self.connections.values()
                    if c.connection_type == conn_type
                )
                for conn_type in set(
                    c.connection_type for c in self.connections.values()
                )
            },
            "connections_by_role": {
                role: sum(
                    1 for c in self.connections.values()
                    if c.role == role
                )
                for role in set(
                    c.role for c in self.connections.values()
                    if c.role
                )
            }
        }
    
    def get_room_info(self, room_name: str) -> Dict[str, Any]:
        """Get information about a specific room"""
        if room_name not in self.room_connections:
            return {"room_name": room_name, "member_count": 0, "members": []}
        
        members = []
        for conn_id in self.room_connections[room_name]:
            if conn_id in self.connections:
                conn_info = self.connections[conn_id]
                members.append({
                    "connection_id": conn_id,
                    "user_id": conn_info.user_id,
                    "username": conn_info.username,
                    "role": conn_info.role
                })
        
        return {
            "room_name": room_name,
            "member_count": len(members),
            "members": members
        }
    
    async def update_ping(self, connection_id: str):
        """Update last ping time for connection"""
        if connection_id in self.connections:
            self.connections[connection_id].last_ping = datetime.utcnow()
    
    async def cleanup_stale_connections(self):
        """Remove connections that haven't pinged in a while"""
        now = datetime.utcnow()
        stale_connections = []
        
        for conn_id, conn_info in self.connections.items():
            if (now - conn_info.last_ping).total_seconds() > self.connection_timeout:
                stale_connections.append(conn_id)
        
        for conn_id in stale_connections:
            logger.warning(f"Removing stale connection: {conn_id}")
            self.disconnect(conn_id)
        
        return len(stale_connections)
    
    async def heartbeat_task(self):
        """Background task to send heartbeats and clean up stale connections"""
        while True:
            try:
                # Clean up stale connections
                cleaned = await self.cleanup_stale_connections()
                if cleaned > 0:
                    logger.info(f"Cleaned up {cleaned} stale connections")
                
                # Send heartbeat to all connections
                heartbeat_message = {
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat(),
                    "stats": self.get_connection_stats()
                }
                
                await self.broadcast(heartbeat_message)
                
                # Wait for next heartbeat
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Heartbeat task error: {e}")
                await asyncio.sleep(self.heartbeat_interval)


# Global manager instance
enhanced_manager = EnhancedWebSocketManager()
