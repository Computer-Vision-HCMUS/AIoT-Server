"""Recommendation services for activity, music, and podcast cards."""

from sqlalchemy.orm import Session

from app.models.emoticare import (
    ActivityFeedback,
    EmotionSession,
    MediaItem,
    MediaSelectionLog,
    RecommendationRequest,
)
from app.services.gemini import gemini_client


EMOTION_ACTIVITY_MAP: dict[str, list[str]] = {
    "stressed": ["breathing", "rest", "movement"],
    "angry": ["breathing", "movement", "rest"],
    "sad": ["rest", "journaling", "breathing"],
    "tired": ["rest", "breathing", "movement"],
    "happy": ["movement", "journaling", "rest"],
    "neutral": ["movement", "breathing", "journaling"],
    "uncertain": ["breathing", "rest", "journaling"],
}

EMOTION_MEDIA_MAP: dict[str, list[str]] = {
    "stressed": ["relax", "sleep"],
    "angry": ["anger_release", "relax"],
    "sad": ["sad_support", "relax"],
    "tired": ["energy_recover", "relax"],
    "happy": ["happy", "focus"],
    "neutral": ["focus", "relax"],
    "uncertain": ["relax", "focus"],
}

ACTIVITY_DESCRIPTIONS: dict[str, str] = {
    "breathing": "Dành 5 phút hít vào 4 nhịp, giữ 7 nhịp và thở ra 8 nhịp. Lặp lại chậm rãi, không cần cố gắng nếu bạn thấy chóng mặt.",
    "rest": "Tạm rời màn hình 10–15 phút, ngồi hoặc nằm ở nơi yên tĩnh. Uống một ngụm nước và cho phép bản thân không cần giải quyết gì ngay lúc này.",
    "movement": "Đứng dậy kéo giãn vai, cổ và lưng trong 2 phút, sau đó đi bộ chậm 5 phút. Mục tiêu là đổi nhịp cơ thể, không phải tập nặng.",
    "journaling": "Viết 3 câu: điều đang xảy ra, cảm xúc của bạn và một việc nhỏ bạn có thể làm tiếp theo. Không cần viết hay, chỉ cần thành thật.",
}


def activity_feedback_score(activity_type: str, user_id: str, db: Session) -> float:
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


def media_feedback_score(media_item_id: str, user_id: str, db: Session) -> float:
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


def _ai_reason(kind: str, emotion_label: str, fallback: str) -> str:
    prompt = (
        "Bạn là trợ lý cảm xúc cho thiết bị TFT nhỏ. "
        f"Viết phần 'Vì sao phù hợp lúc này' bằng tiếng Việt cho gợi ý {kind} "
        f"khi cảm xúc hiện tại là {emotion_label}. Viết 2 câu ấm áp, cụ thể, tổng 180–280 ký tự. "
        "Nêu lợi ích thực tế trong vài phút tới; không chẩn đoán hoặc khẳng định y khoa."
    )
    return gemini_client.generate_text(prompt, fallback=fallback)[:320]


def recommend_action(emotion_label: str, user_id: str, db: Session, *, limit: int = 2) -> list[dict]:
    base_types = EMOTION_ACTIVITY_MAP.get(emotion_label, ["breathing", "rest"])
    all_types = ["breathing", "rest", "movement", "journaling"]
    base_score = {
        activity: max(0, len(base_types) - index)
        for index, activity in enumerate(base_types)
    }
    ranked = sorted(
        all_types,
        key=lambda item: (base_score.get(item, 0), activity_feedback_score(item, user_id, db)),
        reverse=True,
    )

    cards = []
    for activity in ranked[:limit]:
        feedback_score = activity_feedback_score(activity, user_id, db)
        fallback_reason = f"Phù hợp với trạng thái {emotion_label}"
        if feedback_score > 0:
            fallback_reason = f"Ưu tiên vì bạn phản hồi tốt với {activity}"
        cards.append({
            "type": "activity",
            "activity_type": activity,
            "title": activity.capitalize(),
            "body": ACTIVITY_DESCRIPTIONS.get(activity, "Thực hiện hoạt động này để cải thiện tâm trạng"),
            "reason": _ai_reason("hoạt động", emotion_label, fallback_reason),
            "severity": "info",
            "action_id": f"activity:{activity}",
        })
    return cards


def _recommend_media(
    emotion_label: str,
    user_id: str,
    db: Session,
    *,
    media_type: str | None = None,
    categories: list[str] | None = None,
    limit: int = 3,
) -> list[dict]:
    target_categories = categories or EMOTION_MEDIA_MAP.get(emotion_label, ["relax"])
    category_score = {
        category: max(0, len(target_categories) - index)
        for index, category in enumerate(target_categories)
    }
    query = db.query(MediaItem).filter(
        MediaItem.category.in_(target_categories),
        MediaItem.enabled.is_(True),
    )
    if media_type:
        query = query.filter(MediaItem.media_type == media_type)
    ranked = sorted(
        query.all(),
        key=lambda item: (
            category_score.get(item.category, 0),
            media_feedback_score(item.id, user_id, db),
            item.title,
        ),
        reverse=True,
    )

    cards = []
    for item in ranked[:limit]:
        fallback_reason = f"Gợi ý theo cảm xúc {emotion_label}"
        if media_feedback_score(item.id, user_id, db) > 0:
            fallback_reason = "Ưu tiên vì lịch sử nghe phù hợp"
        cards.append({
            "type": item.media_type,
            "media_id": item.id,
            "media_type": item.media_type,
            "title": item.title,
            "creator": item.creator,
            "category": item.category,
            "source_url": item.source_url,
            "body": f"{item.creator or 'Unknown'} · {item.category.replace('_', ' ').title()}",
            "reason": _ai_reason(item.media_type, emotion_label, fallback_reason),
            "duration_sec": item.duration_sec,
            "severity": "info",
            "action_id": f"media:{item.id}",
        })
    return cards


def recommend_music(emotion_label: str, user_id: str, db: Session, *, limit: int = 5) -> list[dict]:
    return _recommend_media(emotion_label, user_id, db, media_type="song", limit=limit)


def recommend_podcast(emotion_label: str, user_id: str, db: Session, *, limit: int = 5) -> list[dict]:
    return _recommend_media(emotion_label, user_id, db, media_type="podcast", limit=limit)


def recommend_media(emotion_label: str, user_id: str, db: Session, *, limit: int = 3) -> list[dict]:
    return _recommend_media(emotion_label, user_id, db, limit=limit)
