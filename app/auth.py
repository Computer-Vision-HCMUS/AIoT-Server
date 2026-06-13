from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models.device import Device

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_device(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_device_token: str | None = Header(default=None),
) -> Device:
    token = credentials.credentials if credentials else x_device_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing device token",
        )

    device = db.query(Device).filter(Device.device_token == token).first()
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device token",
        )
    device.last_seen_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(device)
    return device
