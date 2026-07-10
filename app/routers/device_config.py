"""
Device Config router.

GET /api/device-config — lấy cấu hình rút gọn cho thiết bị
"""

from fastapi import APIRouter, Depends

from app.auth import get_current_device
from app.models.emoticare import Device
from app.schemas import DeviceConfigResponse

router = APIRouter(prefix="/api", tags=["Device Config"])

# Static config returned to all devices
# In production this could be per-user or per-firmware-version
DEVICE_CONFIG = {
    "emotion_labels": [
        "happy", "neutral", "stressed", "sad", "angry", "tired", "uncertain"
    ],
    "confidence_thresholds": {
        "display_label": 0.50,
        "use_for_recommendations": 0.50,
        "high_confidence": 0.75,
    },
    "quality_flags": ["clean", "noisy", "too_short", "low_confidence"],
    "sync_interval_sec": 30,
    "heartbeat_interval_sec": 60,
    "tft_card_max": 5,
    "text_templates": {
        "offline_message": "Chức năng này cần kết nối Internet",
        "sync_pending": "Đang chờ đồng bộ...",
        "waiting_cloud": "Đang lấy dữ liệu từ Cloud...",
        "cloud_result_ready": "Kết quả đã sẵn sàng",
        "limited_data": "Chưa đủ dữ liệu. Hãy check-in thêm nhé!",
    },
    "media_categories": [
        "relax", "focus", "sleep", "happy",
        "sad_support", "anger_release", "energy_recover"
    ],
}


@router.get(
    "/device-config",
    response_model=DeviceConfigResponse,
    summary="Lấy cấu hình rút gọn cho thiết bị",
)
def get_device_config(
    current_device: Device = Depends(get_current_device),
):
    """Trả về threshold, emotion labels và text templates cho thiết bị."""
    return DeviceConfigResponse(
        emotion_labels=DEVICE_CONFIG["emotion_labels"],
        confidence_thresholds=DEVICE_CONFIG["confidence_thresholds"],
        quality_flags=DEVICE_CONFIG["quality_flags"],
        sync_interval_sec=DEVICE_CONFIG["sync_interval_sec"],
        heartbeat_interval_sec=DEVICE_CONFIG["heartbeat_interval_sec"],
        tft_card_max=DEVICE_CONFIG["tft_card_max"],
        text_templates=DEVICE_CONFIG["text_templates"],
        media_categories=DEVICE_CONFIG["media_categories"],
    )
