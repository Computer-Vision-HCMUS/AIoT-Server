"""Recommendation services for activity, music, and podcast cards."""

from sqlalchemy.orm import Session

from app.models.emoticare import (
    ActivityFeedback,
    EmotionSession,
    MediaItem,
    MediaSelectionLog,
    RecommendationRequest,
)


EMOTION_ACTIVITY_MAP: dict[str, list[str]] = {
    "stressed": ["breathing", "rest", "rest_water", "movement", "journaling"],
    "angry": ["breathing", "movement", "rest", "rest_water", "journaling"],
    "sad": ["rest", "journaling", "rest_water", "breathing", "movement"],
    "tired": ["rest_water", "rest", "breathing", "movement", "journaling"],
    "happy": ["movement", "journaling", "breathing", "rest_water", "rest"],
    "neutral": ["movement", "breathing", "journaling", "rest_water", "rest"],
    "uncertain": ["breathing", "rest_water", "rest", "journaling", "movement"],
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
    "rest_water": "Rời màn hình trong 3 phút, uống một cốc nước và nhìn xa khoảng 20 giây. Đây là một nhịp nghỉ ngắn để mắt và cơ thể cùng được thả lỏng.",
}

ACTIVITY_TITLES: dict[str, str] = {
    "breathing": "Thở chậm lại",
    "rest": "Nghỉ một nhịp",
    "movement": "Vận động nhẹ",
    "journaling": "Viết điều đang nghĩ",
    "rest_water": "Uống nước, nghỉ mắt",
}

EMOTION_ACTION_FRAMING: dict[str, tuple[str, str]] = {
    "stressed": ("Hạ nhịp căng thẳng", "Hãy ưu tiên đưa cơ thể về trạng thái chậm và an toàn trước khi quay lại việc đang làm."),
    "angry": ("Xả năng lượng an toàn", "Mục tiêu lúc này là tạo một khoảng dừng để phản ứng bớt bốc đồng và cơ thể dịu lại."),
    "sad": ("Chăm sóc nhẹ nhàng", "Không cần ép mình vui lên ngay; một hành động nhỏ có thể giúp bạn có thêm chỗ dựa trong vài phút tới."),
    "tired": ("Phục hồi năng lượng", "Ưu tiên việc ít tốn sức, giúp mắt, cơ thể và sự tập trung có cơ hội nạp lại từng chút một."),
    "happy": ("Nuôi dưỡng nguồn năng lượng", "Tận dụng trạng thái tích cực này để kết nối cơ thể, ghi nhận điều tốt đẹp và duy trì nhịp sống cân bằng."),
    "neutral": ("Làm mới sự tập trung", "Một nhịp chuyển ngắn có thể giúp bạn tỉnh táo hơn và chọn việc tiếp theo một cách chủ động."),
    "uncertain": ("Neo lại hiện tại", "Khi mọi thứ còn chưa rõ, hãy bắt đầu với điều đơn giản có thể kiểm soát ngay trong vài phút này."),
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


def recommend_action(emotion_label: str, user_id: str, db: Session, *, limit: int = 2) -> list[dict]:
    base_types = EMOTION_ACTIVITY_MAP.get(emotion_label, ["breathing", "rest"])
    all_types = ["breathing", "rest", "movement", "journaling", "rest_water"]
    base_score = {
        activity: max(0, len(base_types) - index)
        for index, activity in enumerate(base_types)
    }
    ranked = sorted(
        all_types,
        key=lambda item: (base_score.get(item, 0), activity_feedback_score("rest" if item == "rest_water" else item, user_id, db)),
        reverse=True,
    )

    cards = []
    framing_title, framing_body = EMOTION_ACTION_FRAMING.get(
        emotion_label,
        ("Chăm sóc bản thân", "Hãy chọn một bước nhỏ, vừa sức và phù hợp với bạn ngay lúc này."),
    )
    for activity in ranked[:limit]:
        feedback_activity = "rest" if activity == "rest_water" else activity
        feedback_score = activity_feedback_score(feedback_activity, user_id, db)
        cards.append({
            "type": "activity",
            "activity_type": feedback_activity,
            "title": f"{framing_title}: {ACTIVITY_TITLES.get(activity, activity.capitalize())}",
            "body": f"{framing_body} {ACTIVITY_DESCRIPTIONS.get(activity, 'Thực hiện hoạt động này để cải thiện tâm trạng')}",
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
        cards.append({
            "type": item.media_type,
            "media_id": item.id,
            "media_type": item.media_type,
            "title": item.title,
            "creator": item.creator,
            "category": item.category,
            "source_url": item.source_url,
            "body": f"{item.creator or 'Unknown'} · {item.category.replace('_', ' ').title()}",
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
