from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_device
from app.database import get_db
from app.models.device import Device
from app.models.visiondrive import DistractionEvent, Trip
from app.schemas import (
    DistractionEventRequest,
    DistractionEventResponse,
    TripEndRequest,
    TripResponse,
    TripStartRequest,
)

router = APIRouter(prefix="/visiondrive", tags=["VisionDrive"])


def require_visiondrive(device: Device) -> None:
    if device.device_type != "visiondrive":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="VisionDrive device token required",
        )


@router.post("/trips", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def start_trip(
    payload: TripStartRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_visiondrive(current_device)
    trip = Trip(device_id=current_device.id, start_time=payload.start_time)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.post("/trips/{trip_id}/end", response_model=TripResponse)
def end_trip(
    trip_id: int,
    payload: TripEndRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_visiondrive(current_device)
    trip = (
        db.query(Trip)
        .filter(Trip.id == trip_id, Trip.device_id == current_device.id)
        .first()
    )
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    trip.end_time = payload.end_time
    trip.safety_score = payload.safety_score
    trip.status = "completed"
    db.commit()
    db.refresh(trip)
    return trip


@router.post(
    "/trips/{trip_id}/distraction-events",
    response_model=DistractionEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_distraction_event(
    trip_id: int,
    payload: DistractionEventRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_visiondrive(current_device)
    trip_exists = (
        db.query(Trip.id)
        .filter(Trip.id == trip_id, Trip.device_id == current_device.id)
        .first()
    )
    if trip_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    event = DistractionEvent(trip_id=trip_id, **payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
