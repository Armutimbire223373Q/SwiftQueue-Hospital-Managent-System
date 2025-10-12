from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import User
from app.routes.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class NavigationRequest(BaseModel):
    current_location: str
    destination: str
    accessibility_needs: str = None

class NavigationRoute(BaseModel):
    steps: List[str]
    estimated_time: int  # in minutes
    distance: float  # in meters
    accessibility_notes: List[str] = []

@router.post("/route", response_model=NavigationRoute)
async def get_navigation_route(
    request: NavigationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # This is a simplified navigation system
    # In a real application, this would integrate with a mapping service
    # or use hospital floor plans

    # Sample navigation logic based on common hospital locations
    routes = {
        ("entrance", "registration"): {
            "steps": ["Walk straight ahead", "Turn left at the information desk", "Registration is on your right"],
            "estimated_time": 2,
            "distance": 50.0,
            "accessibility_notes": ["Wheelchair accessible", "Elevator available"]
        },
        ("registration", "waiting_area"): {
            "steps": ["Exit registration", "Turn right", "Walk to the waiting area"],
            "estimated_time": 1,
            "distance": 30.0,
            "accessibility_notes": ["Wheelchair accessible"]
        },
        ("waiting_area", "consultation_room_1"): {
            "steps": ["From waiting area", "Take the corridor to the right", "Room 101 is the first door on the left"],
            "estimated_time": 3,
            "distance": 75.0,
            "accessibility_notes": ["Wheelchair accessible", "Call button available"]
        },
        ("consultation_room_1", "pharmacy"): {
            "steps": ["Exit consultation room", "Turn left", "Walk to the end of the corridor", "Pharmacy is on the right"],
            "estimated_time": 4,
            "distance": 100.0,
            "accessibility_notes": ["Wheelchair accessible"]
        },
        ("pharmacy", "exit"): {
            "steps": ["Exit pharmacy", "Turn right", "Follow the exit signs", "Main exit is straight ahead"],
            "estimated_time": 3,
            "distance": 80.0,
            "accessibility_notes": ["Wheelchair accessible", "Assistance available"]
        }
    }

    route_key = (request.current_location.lower(), request.destination.lower())
    if route_key not in routes:
        raise HTTPException(status_code=404, detail="Route not found. Please check location names.")

    route = routes[route_key]

    # Add accessibility notes if needed
    if request.accessibility_needs:
        if "wheelchair" in request.accessibility_needs.lower():
            route["accessibility_notes"].append("Wheelchair-accessible route confirmed")
        if "assistance" in request.accessibility_needs.lower():
            route["accessibility_notes"].append("Please request assistance at the information desk")

    return NavigationRoute(**route)

@router.get("/locations", response_model=List[str])
async def get_available_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Return list of navigable locations in the hospital
    return [
        "entrance",
        "registration",
        "waiting_area",
        "consultation_room_1",
        "consultation_room_2",
        "consultation_room_3",
        "pharmacy",
        "laboratory",
        "radiology",
        "emergency",
        "cafeteria",
        "exit"
    ]

@router.post("/emergency", response_model=dict)
async def request_emergency_assistance(
    location: str,
    description: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # In a real system, this would trigger emergency response
    # For now, just log the request

    # TODO: Send notification to staff, log emergency request

    return {
        "message": "Emergency assistance requested",
        "location": location,
        "assistance_en_route": True,
        "estimated_response_time": "2-3 minutes"
    }