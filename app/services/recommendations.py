"""Recommendation services for activity, music, and podcast cards."""

import math
from datetime import datetime, timezone

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
    return min(len(logs), 5) * 0.15 + avg_score


def _recent_media_ids(user_id: str, db: Session, *, limit: int = 8) -> set[str]:
    """Avoid filling a short recommendation list with recently heard items."""
    rows = (
        db.query(MediaSelectionLog.media_item_id)
        .join(MediaSelectionLog.session)
        .filter(EmotionSession.user_id == user_id)
        .order_by(MediaSelectionLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return {item_id for (item_id,) in rows}


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
            "reason": f"Phù hợp với trạng thái {emotion_label}",
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
    # Keep emotion-matching content at the top, but retain the wider catalog
    # as fallback so the client can always receive a full five-item list.
    query = db.query(MediaItem).filter(MediaItem.enabled.is_(True))
    if media_type:
        query = query.filter(MediaItem.media_type == media_type)
    recent_ids = _recent_media_ids(user_id, db)
    ranked = sorted(
        query.all(),
        key=lambda item: (
            0.65 * category_score.get(item.category, 0) / len(target_categories)
            + 0.25 * media_feedback_score(item.id, user_id, db)
            + (-0.30 if item.id in recent_ids else 0.10),
            item.title,
        ),
        reverse=True,
    )

    cards = []
    creator_count: dict[str, int] = {}
    distinct_creators = {item.creator or "" for item in ranked}
    max_per_creator = limit if len(distinct_creators) == 1 else 2
    for item in ranked:
        creator = item.creator or ""
        if creator_count.get(creator, 0) >= max_per_creator:
            continue
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
            "reason": (
                f"Phù hợp với trạng thái {emotion_label}"
                if item.id not in recent_ids
                else "Bạn từng tương tác với nội dung tương tự"
            ),
            "severity": "info",
            "action_id": f"media:{item.id}",
        })
        creator_count[creator] = creator_count.get(creator, 0) + 1
        if len(cards) == limit:
            break
    return cards


def _decayed_weight(created_at: datetime, *, half_life_days: float = 45.0) -> float:
    """Give recent feedback more weight without discarding older preferences."""
    timestamp = created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)
    age_days = max(0.0, (datetime.now(timezone.utc) - timestamp).total_seconds() / 86_400)
    return math.exp(-math.log(2) * age_days / half_life_days)


def _personal_media_signals(user_id: str, db: Session) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    """Return shrinkage-smoothed item/category preference and last-seen age.

    A rating of 3 is neutral.  The denominator adds a small prior so a single
    like cannot dominate the ranker (a common cold-start failure mode).
    """
    rows = (
        db.query(MediaSelectionLog, MediaItem.category)
        .join(MediaSelectionLog.session)
        .join(MediaSelectionLog.media_item)
        .filter(EmotionSession.user_id == user_id)
        .all()
    )
    item_total: dict[str, float] = {}
    item_weight: dict[str, float] = {}
    category_total: dict[str, float] = {}
    category_weight: dict[str, float] = {}
    last_seen_days: dict[str, float] = {}
    now = datetime.now(timezone.utc)
    for log, category in rows:
        created = log.created_at if log.created_at.tzinfo else log.created_at.replace(tzinfo=timezone.utc)
        age_days = max(0.0, (now - created).total_seconds() / 86_400)
        weight = _decayed_weight(created)
        # Missing feedback is neutral evidence: it should not imply a dislike.
        preference = ((log.feedback_score or 3) - 3) / 2
        item_total[log.media_item_id] = item_total.get(log.media_item_id, 0.0) + preference * weight
        item_weight[log.media_item_id] = item_weight.get(log.media_item_id, 0.0) + weight
        category_total[category] = category_total.get(category, 0.0) + preference * weight
        category_weight[category] = category_weight.get(category, 0.0) + weight
        last_seen_days[log.media_item_id] = min(last_seen_days.get(log.media_item_id, float("inf")), age_days)
    item_score = {key: total / (item_weight[key] + 2.0) for key, total in item_total.items()}
    category_score = {key: total / (category_weight[key] + 4.0) for key, total in category_total.items()}
    return item_score, category_score, last_seen_days


def _recommend_media_precise(
    emotion_label: str,
    user_id: str,
    db: Session,
    *,
    media_type: str | None = None,
    categories: list[str] | None = None,
    limit: int = 3,
) -> list[dict]:
    """Contextual hybrid ranker with time-decayed feedback and MMR diversity."""
    target_categories = categories or EMOTION_MEDIA_MAP.get(emotion_label, ["relax"])
    emotion_fit = {category: 1.0 - 0.35 * index for index, category in enumerate(target_categories)}
    item_preference, category_preference, last_seen_days = _personal_media_signals(user_id, db)
    query = db.query(MediaItem).filter(MediaItem.enabled.is_(True))
    if media_type:
        query = query.filter(MediaItem.media_type == media_type)

    scored: list[tuple[MediaItem, float, bool]] = []
    for item in query.all():
        days_since_seen = last_seen_days.get(item.id)
        # Strong penalty for repeats today; it fades smoothly over two weeks.
        novelty = 1.0 if days_since_seen is None else min(1.0, days_since_seen / 14.0) - 1.0
        score = (
            0.56 * emotion_fit.get(item.category, 0.0)
            + 0.22 * item_preference.get(item.id, 0.0)
            + 0.12 * category_preference.get(item.category, 0.0)
            + 0.10 * novelty
        )
        scored.append((item, score, days_since_seen is not None and days_since_seen < 1.0))
    scored.sort(key=lambda row: (row[1], row[0].title), reverse=True)

    # Maximal Marginal Relevance: retain relevance while preventing a short
    # list from collapsing into one category or one creator.
    selected: list[tuple[MediaItem, float, bool]] = []
    candidates = scored[: max(limit * 6, 20)]
    while candidates and len(selected) < limit:
        def mmr(candidate: tuple[MediaItem, float, bool]) -> float:
            item, relevance, _ = candidate
            similarity = max(
                (
                    (0.70 if item.category == chosen.category else 0.0)
                    + (0.30 if item.creator and item.creator == chosen.creator else 0.0)
                    for chosen, _, _ in selected
                ),
                default=0.0,
            )
            return 0.86 * relevance - 0.14 * similarity

        winner = max(candidates, key=mmr)
        selected.append(winner)
        candidates.remove(winner)

    cards = []
    for item, score, recently_seen in selected:
        if item_preference.get(item.id, 0.0) > 0.1:
            reason = "Phù hợp cảm xúc hiện tại và được bạn đánh giá tích cực trước đây"
        elif category_preference.get(item.category, 0.0) > 0.08:
            reason = "Phù hợp cảm xúc hiện tại và chủ đề bạn thường đánh giá tốt"
        elif recently_seen:
            reason = "Phù hợp cảm xúc hiện tại; được giữ lại dù bạn vừa tương tác vì catalog còn hạn chế"
        else:
            reason = f"Phù hợp với trạng thái {emotion_label} và được chọn để tạo sự đa dạng"
        cards.append({
            "type": item.media_type, "media_id": item.id, "media_type": item.media_type,
            "title": item.title, "creator": item.creator, "category": item.category,
            "source_url": item.source_url, "duration_sec": item.duration_sec,
            "body": f"{item.creator or 'Unknown'} · {item.category.replace('_', ' ').title()}",
            "reason": reason, "severity": "info", "action_id": f"media:{item.id}",
            "ranking_score": round(score, 4),
        })
    return cards


def recommend_music(emotion_label: str, user_id: str, db: Session, *, limit: int = 5) -> list[dict]:
    return _recommend_media_precise(emotion_label, user_id, db, media_type="song", limit=limit)


def recommend_podcast(emotion_label: str, user_id: str, db: Session, *, limit: int = 5) -> list[dict]:
    return _recommend_media_precise(emotion_label, user_id, db, media_type="podcast", limit=limit)


def recommend_media(emotion_label: str, user_id: str, db: Session, *, limit: int = 3) -> list[dict]:
    return _recommend_media_precise(emotion_label, user_id, db, limit=limit)
