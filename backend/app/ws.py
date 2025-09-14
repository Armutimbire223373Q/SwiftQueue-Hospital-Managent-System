"""
WebSocket module for real-time queue updates and notifications.
Provides live updates to dashboard and patient interfaces.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
import json
import asyncio
from datetime import datetime
from app.database import get_db
from app.models.models import QueueEntry, Service, ServiceCounter

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.dashboard_connections: List[WebSocket] = []
        self.patient_connections: Dict[str, WebSocket] = {}  # queue_number -> websocket

    async def connect(self, websocket: WebSocket, connection_type: str = "general", identifier: str = None):
        await websocket.accept()
        
        if connection_type == "dashboard":
            self.dashboard_connections.append(websocket)
        elif connection_type == "patient" and identifier:
            self.patient_connections[identifier] = websocket
        else:
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket, connection_type: str = "general", identifier: str = None):
        if connection_type == "dashboard" and websocket in self.dashboard_connections:
            self.dashboard_connections.remove(websocket)
        elif connection_type == "patient" and identifier and identifier in self.patient_connections:
            del self.patient_connections[identifier]
        elif websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            pass  # Connection might be closed

    async def broadcast_to_dashboards(self, message: str):
        disconnected = []
        for connection in self.dashboard_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.dashboard_connections.remove(conn)

    async def notify_patient(self, queue_number: str, message: str):
        if queue_number in self.patient_connections:
            try:
                await self.patient_connections[queue_number].send_text(message)
            except:
                del self.patient_connections[queue_number]

    async def broadcast_queue_update(self, service_id: int, db: Session):
        """Broadcast queue updates to all connected dashboards"""
        try:
            # Get current queue status
            queue_entries = db.query(QueueEntry).filter(
                QueueEntry.service_id == service_id,
                QueueEntry.status.in_(["waiting", "called", "serving"])
            ).order_by(QueueEntry.created_at).all()

            service = db.query(Service).filter(Service.id == service_id).first()
            
            update_data = {
                "type": "queue_update",
                "service_id": service_id,
                "service_name": service.name if service else "Unknown",
                "timestamp": datetime.utcnow().isoformat(),
                "queue_length": len([q for q in queue_entries if q.status == "waiting"]),
                "total_in_system": len(queue_entries),
                "queue_entries": [
                    {
                        "queue_number": entry.queue_number,
                        "patient_name": entry.patient.name if entry.patient else "Unknown",
                        "status": entry.status,
                        "priority": entry.priority,
                        "estimated_wait": entry.ai_predicted_wait,
                        "created_at": entry.created_at.isoformat()
                    }
                    for entry in queue_entries
                ]
            }
            
            await self.broadcast_to_dashboards(json.dumps(update_data))
            
        except Exception as e:
            print(f"Error broadcasting queue update: {e}")

manager = ConnectionManager()

@router.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket, "dashboard")
    try:
        # Send initial data
        services = db.query(Service).all()
        initial_data = {
            "type": "initial_data",
            "timestamp": datetime.utcnow().isoformat(),
            "services": [
                {
                    "id": service.id,
                    "name": service.name,
                    "department": service.department,
                    "queue_length": service.queue_length,
                    "current_wait_time": service.current_wait_time,
                    "staff_count": service.staff_count
                }
                for service in services
            ]
        }
        await manager.send_personal_message(json.dumps(initial_data), websocket)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": datetime.utcnow().isoformat()}),
                        websocket
                    )
                elif message.get("type") == "request_update":
                    service_id = message.get("service_id")
                    if service_id:
                        await manager.broadcast_queue_update(service_id, db)
                        
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Dashboard WebSocket error: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, "dashboard")

@router.websocket("/ws/patient/{queue_number}")
async def patient_websocket(websocket: WebSocket, queue_number: str, db: Session = Depends(get_db)):
    await manager.connect(websocket, "patient", queue_number)
    try:
        # Send initial status
        queue_entry = db.query(QueueEntry).filter(
            QueueEntry.queue_number == int(queue_number)
        ).first()
        
        if queue_entry:
            initial_status = {
                "type": "status_update",
                "queue_number": queue_number,
                "status": queue_entry.status,
                "position": get_queue_position(queue_entry, db),
                "estimated_wait": queue_entry.ai_predicted_wait,
                "service_name": queue_entry.service.name if queue_entry.service else "Unknown",
                "timestamp": datetime.utcnow().isoformat()
            }
            await manager.send_personal_message(json.dumps(initial_status), websocket)
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": datetime.utcnow().isoformat()}),
                        websocket
                    )
                elif message.get("type") == "status_request":
                    # Send updated status
                    queue_entry = db.query(QueueEntry).filter(
                        QueueEntry.queue_number == int(queue_number)
                    ).first()
                    
                    if queue_entry:
                        status_update = {
                            "type": "status_update",
                            "queue_number": queue_number,
                            "status": queue_entry.status,
                            "position": get_queue_position(queue_entry, db),
                            "estimated_wait": queue_entry.ai_predicted_wait,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        await manager.send_personal_message(json.dumps(status_update), websocket)
                        
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Patient WebSocket error: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, "patient", queue_number)

def get_queue_position(queue_entry: QueueEntry, db: Session) -> int:
    """Get the position of a queue entry in the waiting line"""
    earlier_entries = db.query(QueueEntry).filter(
        QueueEntry.service_id == queue_entry.service_id,
        QueueEntry.status == "waiting",
        QueueEntry.created_at < queue_entry.created_at
    ).count()
    return earlier_entries + 1

# Utility functions for triggering WebSocket updates
async def notify_queue_update(service_id: int, db: Session):
    """Trigger a queue update notification"""
    await manager.broadcast_queue_update(service_id, db)

async def notify_patient_called(queue_number: str, counter_name: str):
    """Notify a specific patient that they've been called"""
    message = {
        "type": "patient_called",
        "queue_number": queue_number,
        "counter": counter_name,
        "message": f"Please proceed to {counter_name}",
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.notify_patient(queue_number, json.dumps(message))

async def notify_status_change(queue_number: str, new_status: str, additional_info: dict = None):
    """Notify a patient of status change"""
    message = {
        "type": "status_change",
        "queue_number": queue_number,
        "new_status": new_status,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if additional_info:
        message.update(additional_info)
    
    await manager.notify_patient(queue_number, json.dumps(message))

# Background task for periodic updates
async def periodic_updates():
    """Send periodic updates to all connected clients"""
    while True:
        try:
            # Send heartbeat to all connections
            heartbeat = {
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat(),
                "active_connections": len(manager.active_connections) + len(manager.dashboard_connections) + len(manager.patient_connections)
            }
            
            await manager.broadcast_to_dashboards(json.dumps(heartbeat))
            
            # Wait 30 seconds before next update
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"Periodic update error: {e}")
            await asyncio.sleep(30)

# Start background task when module is imported
# asyncio.create_task(periodic_updates())