"""
EmotiCare AIoT — Device authentication.

Devices authenticate using a token passed via:
  - HTTP header:  X-Device-Token: <token>
  - Bearer:       Authorization: Bearer <token>

The plain token is SHA-256 hashed and compared against device_token_hash in DB.
"""

import hashlib

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models.emoticare import Device

bearer_scheme = HTTPBearer(auto_error=False)


def hash_token(token: str) -> str:
    """Return SHA-256 hex digest of the plain token."""
    return hashlib.sha256(token.encode()).hexdigest()


def get_current_device(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_device_token: str | None = Header(default=None),
) -> Device:
    """Resolve the Device from a token header.

    Lookup is by SHA-256(token) == device_token_hash.
    Updates last_seen_at and sets status = 'online' on every authenticated call.
    """
    plain_token = credentials.credentials if credentials else x_device_token
    if not plain_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing device token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_hash = hash_token(plain_token)
    device = db.query(Device).filter(Device.device_token_hash == token_hash).first()
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update heartbeat fields
    device.last_seen_at = datetime.now(timezone.utc)
    device.status = "online"
    db.commit()
    db.refresh(device)
    return device
