from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_device
from app.database import get_db
from app.models.device import Device
from app.schemas import DeviceRegisterRequest, DeviceRegisterResponse, DeviceResponse

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post(
    "/register",
    response_model=DeviceRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_device(payload: DeviceRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Device).filter(Device.device_id == payload.device_id).first()
    if existing:
        if existing.device_type != payload.device_type:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="device_id already exists with a different device_type",
            )
        existing.last_seen_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing

    device = Device(device_id=payload.device_id, device_type=payload.device_type)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.get("/me", response_model=DeviceResponse)
def get_me(current_device: Device = Depends(get_current_device)):
    return current_device
