"""
Enhanced WebSocket routes for real-time features.
Provides live updates, notifications, presence tracking, and collaborative features.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import json
import asyncio
from datetime import datetime
import logging

from app.database import get_db
from app.models.models import QueueEntry, Service, User, Notification
from app.services.websocket_manager import enhanced_manager
from app.routes.auth import get_current_user_ws

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/enhanced")
async def enhanced_websocket(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    connection_type: str = Query("general"),
    db: Session = Depends(get_db)
):
    """
    Enhanced WebSocket endpoint with full feature support:
    - User authentication
    - Presence tracking
    - Room-based messaging
    - Event broadcasting
    - Real-time notifications
    """
    connection_id = None
    
    try:
        # Authenticate user from token
        user = None
        if token:
            try:
                user = await get_current_user_ws(token, db)
            except Exception as e:
                logger.warning(f"WebSocket authentication failed: {e}")
        
        # Connect with user info
        connection_id = await enhanced_manager.connect(
            websocket=websocket,
            user_id=user.id if user else None,
            username=user.username if user else "anonymous",
            role=user.role if user else None,
            connection_type=connection_type,
            metadata={
                "authenticated": user is not None,
                "ip": websocket.client.host if websocket.client else "unknown"
            }
        )
        
        # Send welcome message
        await enhanced_manager.send_to_connection(connection_id, {
            "type": "welcome",
            "message": f"Welcome to enhanced WebSocket, {user.username if user else 'guest'}!",
            "features": [
                "real-time notifications",
                "presence tracking",
                "room-based chat",
                "queue updates",
                "collaborative features"
            ],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # If user is authenticated, send their notifications
        if user:
            await send_user_notifications(connection_id, user.id, db)
        
        # Message handling loop
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                enhanced_manager.total_messages_received += 1
                
                await handle_message(connection_id, message, user, db)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {connection_id}")
                break
            except json.JSONDecodeError as e:
                await enhanced_manager.send_to_connection(connection_id, {
                    "type": "error",
                    "message": f"Invalid JSON: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.error(f"WebSocket message handling error: {e}")
                await enhanced_manager.send_to_connection(connection_id, {
                    "type": "error",
                    "message": "Internal error processing message",
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    
    finally:
        if connection_id:
            enhanced_manager.disconnect(connection_id)


async def handle_message(
    connection_id: str,
    message: dict,
    user: Optional[User],
    db: Session
):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    
    if message_type == "ping":
        await handle_ping(connection_id, message)
    
    elif message_type == "join_room":
        await handle_join_room(connection_id, message, user)
    
    elif message_type == "leave_room":
        await handle_leave_room(connection_id, message)
    
    elif message_type == "room_message":
        await handle_room_message(connection_id, message, user)
    
    elif message_type == "subscribe_queue":
        await handle_subscribe_queue(connection_id, message, db)
    
    elif message_type == "unsubscribe_queue":
        await handle_unsubscribe_queue(connection_id, message)
    
    elif message_type == "request_queue_update":
        await handle_queue_update_request(connection_id, message, db)
    
    elif message_type == "request_online_users":
        await handle_online_users_request(connection_id)
    
    elif message_type == "request_stats":
        await handle_stats_request(connection_id)
    
    elif message_type == "mark_notification_read":
        await handle_mark_notification_read(connection_id, message, user, db)
    
    elif message_type == "typing_indicator":
        await handle_typing_indicator(connection_id, message, user)
    
    else:
        await enhanced_manager.send_to_connection(connection_id, {
            "type": "error",
            "message": f"Unknown message type: {message_type}",
            "timestamp": datetime.utcnow().isoformat()
        })


async def handle_ping(connection_id: str, message: dict):
    """Handle ping message"""
    await enhanced_manager.update_ping(connection_id)
    await enhanced_manager.send_to_connection(connection_id, {
        "type": "pong",
        "timestamp": datetime.utcnow().isoformat()
    })


async def handle_join_room(connection_id: str, message: dict, user: Optional[User]):
    """Handle join room request"""
    room_name = message.get("room")
    
    if not room_name:
        await enhanced_manager.send_to_connection(connection_id, {
            "type": "error",
            "message": "Room name required",
            "timestamp": datetime.utcnow().isoformat()
        })
        return
    
    enhanced_manager.join_room(connection_id, room_name)
    
    # Notify user
    await enhanced_manager.send_to_connection(connection_id, {
        "type": "room_joined",
        "room": room_name,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Notify room members
    if user:
        await enhanced_manager.broadcast_to_room(room_name, {
            "type": "user_joined_room",
            "room": room_name,
            "user_id": user.id,
            "username": user.username,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_connections={connection_id})


async def handle_leave_room(connection_id: str, message: dict):
    """Handle leave room request"""
    room_name = message.get("room")
    
    if not room_name:
        return
    
    enhanced_manager.leave_room(connection_id, room_name)
    
    await enhanced_manager.send_to_connection(connection_id, {
        "type": "room_left",
        "room": room_name,
        "timestamp": datetime.utcnow().isoformat()
    })


async def handle_room_message(
    connection_id: str,
    message: dict,
    user: Optional[User]
):
    """Handle room message broadcast"""
    room_name = message.get("room")
    content = message.get("content")
    
    if not room_name or not content:
        await enhanced_manager.send_to_connection(connection_id, {
            "type": "error",
            "message": "Room and content required",
            "timestamp": datetime.utcnow().isoformat()
        })
        return
    
    if not user:
        await enhanced_manager.send_to_connection(connection_id, {
            "type": "error",
            "message": "Authentication required for room messages",
            "timestamp": datetime.utcnow().isoformat()
        })
        return
    
    # Broadcast to room
    broadcast_message = {
        "type": "room_message",
        "room": room_name,
        "user_id": user.id,
        "username": user.username,
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    sent_count = await enhanced_manager.broadcast_to_room(
        room_name,
        broadcast_message
    )
    
    # Confirm to sender
    await enhanced_manager.send_to_connection(connection_id, {
        "type": "message_sent",
        "room": room_name,
        "recipients": sent_count,
        "timestamp": datetime.utcnow().isoformat()
    })


async def handle_subscribe_queue(connection_id: str, message: dict, db: Session):
    """Handle queue subscription"""
    queue_id = message.get("queue_id")
    service_id = message.get("service_id")
    department = message.get("department")
    
    room_name = None
    if queue_id:
        room_name = f"queue_{queue_id}"
    elif service_id:
        room_name = f"service_{service_id}"
    elif department:
        room_name = f"department_{department}"
    
    if not room_name:
        await enhanced_manager.send_to_connection(connection_id, {
            "type": "error",
            "message": "Queue ID, service ID, or department required",
            "timestamp": datetime.utcnow().isoformat()
        })
        return
    
    enhanced_manager.join_room(connection_id, room_name)
    
    # Send initial queue data
    if service_id:
        await send_queue_update(room_name, service_id, db)
    
    await enhanced_manager.send_to_connection(connection_id, {
        "type": "subscribed",
        "room": room_name,
        "timestamp": datetime.utcnow().isoformat()
    })


async def handle_unsubscribe_queue(connection_id: str, message: dict):
    """Handle queue unsubscription"""
    room_name = message.get("room")
    
    if room_name:
        enhanced_manager.leave_room(connection_id, room_name)
        
        await enhanced_manager.send_to_connection(connection_id, {
            "type": "unsubscribed",
            "room": room_name,
            "timestamp": datetime.utcnow().isoformat()
        })


async def handle_queue_update_request(
    connection_id: str,
    message: dict,
    db: Session
):
    """Handle request for queue update"""
    service_id = message.get("service_id")
    
    if not service_id:
        await enhanced_manager.send_to_connection(connection_id, {
            "type": "error",
            "message": "Service ID required",
            "timestamp": datetime.utcnow().isoformat()
        })
        return
    
    room_name = f"service_{service_id}"
    await send_queue_update(room_name, service_id, db)


async def handle_online_users_request(connection_id: str):
    """Handle request for online users list"""
    online_users = enhanced_manager.get_online_users()
    
    await enhanced_manager.send_to_connection(connection_id, {
        "type": "online_users",
        "users": online_users,
        "count": len(online_users),
        "timestamp": datetime.utcnow().isoformat()
    })


async def handle_stats_request(connection_id: str):
    """Handle request for connection statistics"""
    stats = enhanced_manager.get_connection_stats()
    
    await enhanced_manager.send_to_connection(connection_id, {
        "type": "stats",
        "data": stats,
        "timestamp": datetime.utcnow().isoformat()
    })


async def handle_mark_notification_read(
    connection_id: str,
    message: dict,
    user: Optional[User],
    db: Session
):
    """Handle mark notification as read"""
    if not user:
        return
    
    notification_id = message.get("notification_id")
    
    if not notification_id:
        return
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user.id
    ).first()
    
    if notification:
        notification.is_read = True
        db.commit()
        
        await enhanced_manager.send_to_connection(connection_id, {
            "type": "notification_marked_read",
            "notification_id": notification_id,
            "timestamp": datetime.utcnow().isoformat()
        })


async def handle_typing_indicator(
    connection_id: str,
    message: dict,
    user: Optional[User]
):
    """Handle typing indicator"""
    if not user:
        return
    
    room_name = message.get("room")
    is_typing = message.get("is_typing", True)
    
    if not room_name:
        return
    
    await enhanced_manager.broadcast_to_room(room_name, {
        "type": "typing_indicator",
        "room": room_name,
        "user_id": user.id,
        "username": user.username,
        "is_typing": is_typing,
        "timestamp": datetime.utcnow().isoformat()
    }, exclude_connections={connection_id})


async def send_user_notifications(connection_id: str, user_id: int, db: Session):
    """Send unread notifications to user"""
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).order_by(Notification.created_at.desc()).limit(50).all()
    
    if notifications:
        await enhanced_manager.send_to_connection(connection_id, {
            "type": "notifications",
            "notifications": [
                {
                    "id": n.id,
                    "title": n.title,
                    "message": n.message,
                    "type": n.type,
                    "created_at": n.created_at.isoformat()
                }
                for n in notifications
            ],
            "count": len(notifications),
            "timestamp": datetime.utcnow().isoformat()
        })


async def send_queue_update(room_name: str, service_id: int, db: Session):
    """Send queue update to room"""
    try:
        service = db.query(Service).filter(Service.id == service_id).first()
        
        if not service:
            return
        
        queue_entries = db.query(QueueEntry).filter(
            QueueEntry.service_id == service_id,
            QueueEntry.status.in_(["waiting", "called", "serving"])
        ).order_by(QueueEntry.created_at).all()
        
        update_data = {
            "type": "queue_update",
            "room": room_name,
            "service_id": service_id,
            "service_name": service.name,
            "timestamp": datetime.utcnow().isoformat(),
            "queue_length": len([q for q in queue_entries if q.status == "waiting"]),
            "currently_serving": len([q for q in queue_entries if q.status == "serving"]),
            "queue_entries": [
                {
                    "queue_number": entry.queue_number,
                    "status": entry.status,
                    "priority": entry.priority,
                    "created_at": entry.created_at.isoformat()
                }
                for entry in queue_entries
            ]
        }
        
        await enhanced_manager.broadcast_to_room(room_name, update_data)
        
    except Exception as e:
        logger.error(f"Error sending queue update: {e}")


# Utility functions for external use
async def notify_queue_change(service_id: int, db: Session):
    """Notify all subscribers of a queue change"""
    room_name = f"service_{service_id}"
    await send_queue_update(room_name, service_id, db)


async def notify_user_event(user_id: int, event_type: str, data: dict):
    """Notify a specific user of an event"""
    message = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await enhanced_manager.send_to_user(user_id, message)


async def broadcast_system_message(message: str, level: str = "info"):
    """Broadcast system message to all connected users"""
    broadcast_message = {
        "type": "system_message",
        "level": level,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await enhanced_manager.broadcast(broadcast_message)


# Start heartbeat task
@router.on_event("startup")
async def start_heartbeat():
    """Start WebSocket heartbeat task"""
    asyncio.create_task(enhanced_manager.heartbeat_task())
    logger.info("WebSocket heartbeat task started")
