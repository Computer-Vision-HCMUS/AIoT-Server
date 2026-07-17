"""
Recommendations router.

POST /api/recommendations/request — yêu cầu Cloud gợi ý hoạt động hỗ trợ cảm xúc
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_device
from app.database import get_db
from app.models.emoticare import (
    ActivityFeedback,
    Device,
    EmotionSession,
    MediaItem,
    MediaSelectionLog,
    RecommendationRequest,
)
from app.schemas import RecommendationRequestPayload, RecommendationResponse
from app.services.recommendations import recommend_action

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

# Mapping emotion label → recommended activity types (priority order)
EMOTION_ACTIVITY_MAP: dict[str, list[str]] = {
    "stressed":   ["breathing", "rest", "movement"],
    "angry":      ["breathing", "movement", "rest"],
    "sad":        ["rest", "journaling", "breathing"],
    "tired":      ["rest", "breathing", "movement"],
    "happy":      ["movement", "journaling", "rest"],
    "neutral":    ["movement", "breathing", "journaling"],
    "uncertain":  ["breathing", "rest", "journaling"],
}

# Mapping emotion label → recommended media categories (priority order)
EMOTION_MEDIA_MAP: dict[str, list[str]] = {
    "stressed":   ["relax", "sleep"],
    "angry":      ["anger_release", "relax"],
    "sad":        ["sad_support", "relax"],
    "tired":      ["energy_recover", "relax"],
    "happy":      ["happy", "focus"],
    "neutral":    ["focus", "relax"],
    "uncertain":  ["relax", "focus"],
}

ACTIVITY_DESCRIPTIONS: dict[str, str] = {
    "breathing":  "Hít thở sâu 4-7-8 trong 5 phút",
    "rest":       "Nghỉ ngơi hoàn toàn 10-15 phút",
    "movement":   "Vận động nhẹ — đứng dậy, kéo giãn hoặc đi bộ ngắn",
    "journaling": "Viết 3 câu ngắn về cảm xúc hiện tại",
}


def _activity_feedback_score(activity_type: str, user_id: str, db: Session) -> float:
    feedbacks = (
        db.query(ActivityFeedback)
        .join(ActivityFeedback.recommendation)
        .join(RecommendationRequest.session)
        .filter(
            EmotionSession.user_id == user_id,
            ActivityFeedback.activity_type == activity_type,
        )
        .all()
    )
    if not feedbacks:
        return 0.0
    selected_bonus = sum(1 for item in feedbacks if item.selected) * 0.25
    scored = [item.feedback_score for item in feedbacks if item.feedback_score is not None]
    avg_score = (sum(scored) / len(scored) - 3.0) * 0.6 if scored else 0.0
    return selected_bonus + avg_score


def _rank_activity_types(emotion_label: str, user_id: str, db: Session) -> list[str]:
    base_types = EMOTION_ACTIVITY_MAP.get(emotion_label, ["breathing", "rest"])
    all_types = ["breathing", "rest", "movement", "journaling"]
    base_score = {activity: max(0, len(base_types) - index) for index, activity in enumerate(base_types)}
    ranked = sorted(
        all_types,
        key=lambda item: (base_score.get(item, 0), _activity_feedback_score(item, user_id, db)),
        reverse=True,
    )
    return ranked


def _build_activity_cards(emotion_label: str, user_id: str, db: Session) -> list[dict]:
    """Build up to 2 activity cards using emotion rules and user feedback."""
    activity_types = _rank_activity_types(emotion_label, user_id, db)
    cards = []
    for activity in activity_types[:2]:
        feedback_score = _activity_feedback_score(activity, user_id, db)
        reason = f"Phù hợp với trạng thái {emotion_label}"
        if feedback_score > 0:
            reason = f"Ưu tiên vì trước đây bạn phản hồi tốt với {activity}"
        cards.append({
            "type": "activity",
            "activity_type": activity,
            "title": activity.capitalize(),
            "body": ACTIVITY_DESCRIPTIONS.get(activity, "Thực hiện hoạt động này để cải thiện tâm trạng"),
            "reason": reason,
            "severity": "info",
            "action_id": f"activity:{activity}",
        })
    return cards


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


def _build_media_cards(emotion_label: str, user_id: str, db: Session, limit: int = 3) -> list[dict]:
    """Build media cards from DB using emotion category rules and feedback."""
    categories = EMOTION_MEDIA_MAP.get(emotion_label, ["relax"])
    category_score = {category: max(0, len(categories) - index) for index, category in enumerate(categories)}
    items = (
        db.query(MediaItem)
        .filter(MediaItem.category.in_(categories), MediaItem.enabled.is_(True))
        .all()
    )
    ranked = sorted(
        items,
        key=lambda item: (
            category_score.get(item.category, 0),
            _media_feedback_score(item.id, user_id, db),
            item.title,
        ),
        reverse=True,
    )

    cards = []
    for item in ranked[:limit]:
        feedback_score = _media_feedback_score(item.id, user_id, db)
        reason = f"Gợi ý theo cảm xúc {emotion_label}"
        if feedback_score > 0:
            reason = "Ưu tiên vì lịch sử nghe/đánh giá của bạn phù hợp"
        cards.append({
            "type": item.media_type,
            "media_id": item.id,
            "title": item.title,
            "body": f"{item.creator or 'Unknown'} · {item.category.replace('_', ' ').title()}",
            "reason": reason,
            "duration_sec": item.duration_sec,
            "severity": "info",
            "action_id": f"media:{item.id}",
        })
    return cards


@router.post(
    "/request",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Yêu cầu Cloud gợi ý hoạt động, bài hát và podcast",
)
def request_recommendation(
    payload: RecommendationRequestPayload,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    """
    Nhận emotion context và trả về 1-5 recommendation cards rút gọn cho TFT.
    Cards gồm: hoạt động (activity) + bài hát/podcast (song/podcast).
    """
    # Verify session belongs to current device
    session = (
        db.query(EmotionSession)
        .filter(
            EmotionSession.id == payload.session_id,
            EmotionSession.device_id == current_device.id,
        )
        .first()
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emotion session not found or does not belong to this device",
        )

    emotion_label = session.emotion_label

    # The simulator does not ship a media library yet, so return five actionable
    # wellbeing activities rather than mixing in unavailable music or podcasts.
    all_cards = recommend_action(emotion_label, current_device.user_id, db, limit=5)

    response_payload = {
        "emotion_label": emotion_label,
        "cards": all_cards,
    }

    # Persist the recommendation request
    reco = RecommendationRequest(
        id=str(uuid.uuid4()),
        session_id=session.id,
        request_payload={"session_id": payload.session_id, "emotion_label": emotion_label},
        response_payload=response_payload,
        status="success" if all_cards else "limited",
        created_at=datetime.now(timezone.utc),
    )
    db.add(reco)
    db.commit()
    db.refresh(reco)

    return RecommendationResponse(
        recommendation_id=reco.id,
        emotion_label=emotion_label,
        cards=all_cards,
        status=reco.status,
    )


@router.post(
    "/action",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Gợi ý hoạt động hỗ trợ cảm xúc",
)
def request_action_recommendation(
    payload: RecommendationRequestPayload,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    session = (
        db.query(EmotionSession)
        .filter(
            EmotionSession.id == payload.session_id,
            EmotionSession.device_id == current_device.id,
        )
        .first()
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emotion session not found or does not belong to this device",
        )

    cards = recommend_action(session.emotion_label, current_device.user_id, db, limit=5)
    response_payload = {
        "emotion_label": session.emotion_label,
        "cards": cards,
    }
    reco = RecommendationRequest(
        id=str(uuid.uuid4()),
        session_id=session.id,
        request_payload={
            "session_id": payload.session_id,
            "emotion_label": session.emotion_label,
            "recommendation_type": "action",
        },
        response_payload=response_payload,
        status="success" if cards else "limited",
        created_at=datetime.now(timezone.utc),
    )
    db.add(reco)
    db.commit()
    db.refresh(reco)

    return RecommendationResponse(
        recommendation_id=reco.id,
        emotion_label=session.emotion_label,
        cards=cards,
        status=reco.status,
    )


@router.get(
    "",
    summary="Liệt kê recommendation requests gần nhất của thiết bị",
)
def list_recommendations(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    items = (
        db.query(RecommendationRequest)
        .join(RecommendationRequest.session)
        .filter(EmotionSession.device_id == current_device.id)
        .order_by(RecommendationRequest.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "items": [
            {
                "id": item.id,
                "session_id": item.session_id,
                "status": item.status,
                "request_payload": item.request_payload,
                "response_payload": item.response_payload,
                "created_at": item.created_at,
            }
            for item in items
        ]
    }
