"""
Media router.

GET  /api/media/categories       — lấy danh sách 7 category
POST /api/media/recommendations  — lấy bài hát/podcast theo category và intent
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_device
from app.database import get_db
from app.models.emoticare import Device, EmotionSession, MediaItem, MediaSelectionLog
from app.schemas import (
    MediaCategoriesResponse,
    MediaRecommendationRequest,
    MediaRecommendationResponse,
)
from app.services.recommendations import recommend_music, recommend_podcast

router = APIRouter(prefix="/api/media", tags=["Media"])

CATEGORY_META: dict[str, dict] = {
    "relax": {
        "label": "Thư giãn",
        "description": "Nhạc nhẹ, ambient, podcast thở chậm",
        "use_case": "Khi căng thẳng",
    },
    "focus": {
        "label": "Tập trung",
        "description": "Nhạc không lời, white noise, podcast tập trung",
        "use_case": "Khi cần học / làm việc",
    },
    "sleep": {
        "label": "Ngủ nghỉ",
        "description": "Nhạc chậm, sleep story, podcast thiền ngủ",
        "use_case": "Khi cần nghỉ ngơi",
    },
    "happy": {
        "label": "Vui vẻ",
        "description": "Nhạc tích cực, podcast truyền cảm hứng",
        "use_case": "Khi muốn duy trì năng lượng tốt",
    },
    "sad_support": {
        "label": "Xoa dịu buồn bã",
        "description": "Nhạc ấm, podcast chia sẻ cảm xúc",
        "use_case": "Khi buồn bã",
    },
    "anger_release": {
        "label": "Giải tỏa tức giận",
        "description": "Nhạc grounding, podcast kiểm soát cảm xúc",
        "use_case": "Khi tức giận",
    },
    "energy_recover": {
        "label": "Phục hồi năng lượng",
        "description": "Nhạc nhẹ có nhịp vừa, podcast self-care",
        "use_case": "Khi mệt mỏi",
    },
}

EMOTION_CATEGORY_MAP: dict[str, list[str]] = {
    "stressed": ["relax", "sleep"],
    "angry": ["anger_release", "relax"],
    "sad": ["sad_support", "relax"],
    "tired": ["energy_recover", "sleep"],
    "happy": ["happy", "focus"],
    "neutral": ["focus", "relax"],
    "uncertain": ["relax", "focus"],
}

INTENT_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "relax": ["relax", "calm", "thư giãn", "bình tĩnh", "căng thẳng"],
    "focus": ["focus", "tập trung", "học", "làm việc"],
    "sleep": ["sleep", "ngủ", "nghỉ", "mệt"],
    "happy": ["happy", "vui", "tích cực"],
    "sad_support": ["sad", "buồn", "cô đơn", "xoa dịu"],
    "anger_release": ["angry", "giận", "tức", "bực"],
    "energy_recover": ["energy", "năng lượng", "kiệt sức", "uể oải"],
}


def _intent_categories(intent: str | None) -> list[str]:
    if not intent:
        return []
    lower = intent.lower()
    return [
        category
        for category, keywords in INTENT_CATEGORY_KEYWORDS.items()
        if any(keyword in lower for keyword in keywords)
    ]


def _media_feedback_score(media_item_id: str, user_id: str, db: Session) -> float:
    logs = (
        db.query(MediaSelectionLog)
        .join(MediaSelectionLog.session)
        .filter(
            EmotionSession.user_id == user_id,
            MediaSelectionLog.media_item_id == media_item_id,
        )
        .all()
    )
    if not logs:
        return 0.0
    scored = [item.feedback_score for item in logs if item.feedback_score is not None]
    avg_score = (sum(scored) / len(scored) - 3.0) * 0.8 if scored else 0.0
    return len(logs) * 0.15 + avg_score


@router.get(
    "/categories",
    response_model=MediaCategoriesResponse,
    summary="Lấy danh sách category bài hát/podcast",
)
def get_media_categories(
    current_device: Device = Depends(get_current_device),
):
    """Trả về 7 category media với label và mô tả ngắn để hiển thị trên TFT."""
    categories = [
        {
            "id": cat_id,
            "label": meta["label"],
            "description": meta["description"],
            "use_case": meta["use_case"],
        }
        for cat_id, meta in CATEGORY_META.items()
    ]
    return MediaCategoriesResponse(categories=categories)


@router.post(
    "/recommendations",
    response_model=MediaRecommendationResponse,
    summary="Lấy bài hát/podcast theo chủ đích và category",
)
def get_media_recommendations(
    payload: MediaRecommendationRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    """
    Lọc media items theo category, media_type (song | podcast | both) và
    emotion_label tuỳ chọn. Trả về tối đa 5 card rút gọn cho TFT.
    """
    query = db.query(MediaItem).filter(MediaItem.enabled.is_(True))
    intent_categories = _intent_categories(payload.user_intent)

    if payload.category:
        query = query.filter(MediaItem.category == payload.category)
    elif intent_categories:
        query = query.filter(MediaItem.category.in_(intent_categories))
    elif payload.emotion_label:
        query = query.filter(
            MediaItem.category.in_(EMOTION_CATEGORY_MAP.get(payload.emotion_label, ["relax"]))
        )

    if payload.media_type and payload.media_type != "both":
        query = query.filter(MediaItem.media_type == payload.media_type)

    items = query.all()
    preferred_categories = (
        [payload.category] if payload.category else
        intent_categories or EMOTION_CATEGORY_MAP.get(payload.emotion_label or "neutral", ["relax"])
    )
    category_score = {
        category: max(0, len(preferred_categories) - index)
        for index, category in enumerate(preferred_categories)
    }
    ranked_items = sorted(
        items,
        key=lambda item: (
            category_score.get(item.category, 0),
            _media_feedback_score(item.id, current_device.user_id, db),
            item.title,
        ),
        reverse=True,
    )[:5]

    cards = [
        {
            "media_id": item.id,
            "media_type": item.media_type,
            "title": item.title,
            "creator": item.creator,
            "category": item.category,
            "duration_sec": item.duration_sec,
            "source_url": item.source_url,
            "reason": (
                f"Khớp chủ đích: {payload.user_intent}"
                if payload.user_intent
                else f"Phù hợp với nhóm {item.category.replace('_', ' ')}"
            ),
            "severity": "info",
            "action_id": f"media:{item.id}",
        }
        for item in ranked_items
    ]

    return MediaRecommendationResponse(
        category=payload.category,
        media_type=payload.media_type or "both",
        cards=cards,
    )


@router.post(
    "/music/recommend",
    response_model=MediaRecommendationResponse,
    summary="Gợi ý nhạc theo cảm xúc",
)
def recommend_music_endpoint(
    payload: MediaRecommendationRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    emotion_label = payload.emotion_label or "neutral"
    cards = recommend_music(emotion_label, current_device.user_id, db, limit=5)
    return MediaRecommendationResponse(
        category=payload.category,
        media_type="song",
        cards=cards,
    )


@router.post(
    "/podcast/recommend",
    response_model=MediaRecommendationResponse,
    summary="Gợi ý podcast theo cảm xúc",
)
def recommend_podcast_endpoint(
    payload: MediaRecommendationRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    emotion_label = payload.emotion_label or "neutral"
    cards = recommend_podcast(emotion_label, current_device.user_id, db, limit=5)
    return MediaRecommendationResponse(
        category=payload.category,
        media_type="podcast",
        cards=cards,
    )


@router.get(
    "/history",
    summary="Liệt kê media selection logs gần nhất của thiết bị",
)
def list_media_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    logs = (
        db.query(MediaSelectionLog)
        .join(MediaSelectionLog.session)
        .join(MediaSelectionLog.media_item)
        .filter(EmotionSession.device_id == current_device.id)
        .order_by(MediaSelectionLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "items": [
            {
                "id": item.id,
                "session_id": item.session_id,
                "media_item_id": item.media_item_id,
                "title": item.media_item.title,
                "media_type": item.media_item.media_type,
                "selected_category": item.selected_category,
                "user_intent": item.user_intent,
                "feedback_score": item.feedback_score,
                "created_at": item.created_at,
            }
            for item in logs
        ]
    }
