"""
Feedback router.

POST /api/feedback/activity — gửi lựa chọn / đánh giá hoạt động
POST /api/feedback/media    — gửi lựa chọn / đánh giá bài hát hoặc podcast
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
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
from app.schemas import (
    ActivityFeedbackRequest,
    FeedbackSavedResponse,
    MediaFeedbackRequest,
)

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


@router.post(
    "/activity",
    response_model=FeedbackSavedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gửi lựa chọn / đánh giá hoạt động",
)
def submit_activity_feedback(
    payload: ActivityFeedbackRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    """Lưu feedback hoạt động người dùng chọn từ recommendation card."""
    # Verify recommendation belongs to this device (via session.device_id)
    reco = (
        db.query(RecommendationRequest)
        .join(RecommendationRequest.session)
        .filter(
            RecommendationRequest.id == payload.recommendation_id,
            EmotionSession.device_id == current_device.id,
        )
        .first()
    )
    if reco is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    # Validate feedback_score range
    if payload.feedback_score is not None and not (1 <= payload.feedback_score <= 5):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="feedback_score must be between 1 and 5",
        )

    feedback = ActivityFeedback(
        id=str(uuid.uuid4()),
        recommendation_id=payload.recommendation_id,
        activity_type=payload.activity_type,
        selected=payload.selected,
        feedback_score=payload.feedback_score,
        created_at=datetime.now(timezone.utc),
    )
    db.add(feedback)
    db.commit()

    return FeedbackSavedResponse(
        feedback_id=feedback.id,
        saved=True,
    )


@router.post(
    "/media",
    response_model=FeedbackSavedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gửi lựa chọn / đánh giá bài hát hoặc podcast",
)
def submit_media_feedback(
    payload: MediaFeedbackRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    """Lưu media selection log và feedback score người dùng gửi về."""
    # Validate media item exists
    media_item = (
        db.query(MediaItem)
        .filter(MediaItem.id == payload.media_item_id)
        .first()
    )
    if media_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media item not found",
        )

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
            detail="Emotion session not found",
        )

    if payload.feedback_score is not None and not (1 <= payload.feedback_score <= 5):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="feedback_score must be between 1 and 5",
        )

    log = MediaSelectionLog(
        id=str(uuid.uuid4()),
        session_id=payload.session_id,
        media_item_id=payload.media_item_id,
        user_intent=payload.user_intent,
        selected_category=media_item.category,
        feedback_score=payload.feedback_score,
        created_at=datetime.now(timezone.utc),
    )
    db.add(log)
    db.commit()

    return FeedbackSavedResponse(
        feedback_id=log.id,
        saved=True,
    )
