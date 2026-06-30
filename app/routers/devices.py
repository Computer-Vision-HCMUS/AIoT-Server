"""
Devices router — pair and heartbeat.

POST /api/devices/pair      — ghép thiết bị với user bằng pairing_code
POST /api/devices/heartbeat — cập nhật trạng thái online và firmware
"""

import secrets
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_device, hash_token
from app.database import get_db
from app.models.emoticare import Device, User
from app.schemas import (
    DeviceHeartbeatRequest,
    DeviceHeartbeatResponse,
    DevicePairRequest,
    DevicePairResponse,
)

router = APIRouter(prefix="/api/devices", tags=["Devices"])

CONFIG_VERSION = "emoticare-edge-config-v1"


@router.post(
    "/pair",
    response_model=DevicePairResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ghép thiết bị với user bằng pairing code",
)
def pair_device(payload: DevicePairRequest, db: Session = Depends(get_db)):
    """
    Thiết bị gửi pairing_code để liên kết với tài khoản user.
    Trả về device_token một lần duy nhất — thiết bị phải lưu lại.
    """
    user = db.query(User).filter(User.pairing_code == payload.pairing_code).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pairing code not found or already used",
        )

    # Generate plain token — returned once, then hashed for storage
    plain_token = secrets.token_hex(32)
    token_hash = hash_token(plain_token)

    device = Device(
        id=str(uuid.uuid4()),
        user_id=user.id,
        name=payload.device_name,
        device_token_hash=token_hash,
        firmware_version=payload.firmware_version,
        status="online",
        last_seen_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    db.add(device)
    db.commit()
    db.refresh(device)

    return DevicePairResponse(
        device_id=device.id,
        user_id=user.id,
        device_name=device.name,
        device_token=plain_token,  # plain token returned once
        status=device.status,
        paired_at=device.created_at,
    )


@router.post(
    "/heartbeat",
    response_model=DeviceHeartbeatResponse,
    summary="Cập nhật trạng thái online và firmware version",
)
def heartbeat(
    payload: DeviceHeartbeatRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    """
    Thiết bị gửi heartbeat định kỳ để Cloud biết trạng thái.
    Trả về server_time để thiết bị đồng bộ đồng hồ.
    """
    if payload.firmware_version:
        current_device.firmware_version = payload.firmware_version

    db.commit()

    return DeviceHeartbeatResponse(
        device_id=current_device.id,
        server_time=datetime.now(timezone.utc),
        status=current_device.status,
        config_version=CONFIG_VERSION,
    )
