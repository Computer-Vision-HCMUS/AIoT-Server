"""
Reports router.

GET  /api/reports/tft-summary — lấy report rút gọn theo period
POST /api/reports/generate    — yêu cầu tạo report mới
"""

import uuid
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_device
from app.database import get_db
from app.models.emoticare import (
    ActivityFeedback,
    ConversationRequest,
    Device,
    EmotionSession,
    MediaSelectionLog,
    RecommendationRequest,
    TftReport,
)
from app.schemas import ReportGenerateRequest, ReportGenerateResponse, TftSummaryResponse

router = APIRouter(prefix="/api/reports", tags=["Reports"])

MIN_SESSIONS_FOR_FULL_REPORT = 3
NEGATIVE_EMOTIONS = {"stressed", "angry", "sad", "tired"}


def _period_bounds(period_type: str) -> tuple[date, date]:
    """Return (start, end) UTC dates for the requested period."""
    now = datetime.now(timezone.utc)
    if period_type == "daily":
        start = now.date()
        end = start + timedelta(days=1)
    elif period_type == "weekly":
        # Week starts on Monday
        start = (now - timedelta(days=now.weekday())).date()
        end = start + timedelta(weeks=1)
    elif period_type == "monthly":
        start = now.date().replace(day=1)
        # First day of next month
        if now.month == 12:
            end = start.replace(year=now.year + 1, month=1)
        else:
            end = start.replace(month=now.month + 1)
    else:  # yearly
        start = now.date().replace(month=1, day=1)
        end = start.replace(year=now.year + 1)
    return start, end


def _as_utc_datetime(value: date) -> datetime:
    return datetime.combine(value, time.min, tzinfo=timezone.utc)


def _avg(values: list[int]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 1)


def _negative_ratio(sessions: list[EmotionSession]) -> float:
    if not sessions:
        return 0.0
    return sum(1 for item in sessions if item.emotion_label in NEGATIVE_EMOTIONS) / len(sessions)


def _trend_card(sessions: list[EmotionSession]) -> dict:
    if len(sessions) < 2:
        return {
            "title": "Xu hướng cảm xúc",
            "body": "Chưa đủ dữ liệu để so sánh xu hướng.",
            "severity": "warn",
            "action_id": "report:trend",
        }
    midpoint = max(1, len(sessions) // 2)
    older = sessions[:midpoint]
    recent = sessions[midpoint:] or sessions[-1:]
    older_negative = _negative_ratio(older)
    recent_negative = _negative_ratio(recent)
    delta = recent_negative - older_negative
    if delta <= -0.15:
        body = "Tỷ lệ cảm xúc khó chịu giảm so với phần đầu kỳ."
        severity = "info"
    elif delta >= 0.15:
        body = "Tỷ lệ cảm xúc khó chịu tăng, nên ưu tiên hoạt động hỗ trợ ngắn."
        severity = "warn"
    else:
        body = "Cảm xúc khá ổn định trong kỳ này."
        severity = "info"
    return {
        "title": "Xu hướng cảm xúc",
        "body": body,
        "severity": severity,
        "action_id": "report:trend",
    }


def _generate_report(
    user_id: str,
    device_id: str,
    period_type: str,
    db: Session,
) -> TftReport:
    """Build and persist a TftReport for the given period."""
    period_start, period_end = _period_bounds(period_type)
    period_start_dt = _as_utc_datetime(period_start)
    period_end_dt = _as_utc_datetime(period_end)

    sessions = (
        db.query(EmotionSession)
        .filter(
            EmotionSession.user_id == user_id,
            EmotionSession.device_id == device_id,
            EmotionSession.client_created_at >= period_start_dt,
            EmotionSession.client_created_at < period_end_dt,
        )
        .order_by(EmotionSession.client_created_at.asc())
        .all()
    )

    # Fallback: ESP32 has no RTC so client_created_at is always anchored to 2025-01-01.
    # If the primary filter returns nothing, retry using the server-assigned created_at
    # (which is always an accurate UTC wall-clock timestamp).
    if not sessions:
        sessions = (
            db.query(EmotionSession)
            .filter(
                EmotionSession.user_id == user_id,
                EmotionSession.device_id == device_id,
                EmotionSession.created_at >= period_start_dt,
                EmotionSession.created_at < period_end_dt,
            )
            .order_by(EmotionSession.created_at.asc())
            .all()
        )
    session_ids = [session.id for session in sessions]
    recommendation_count = 0
    activity_scores: list[int] = []
    media_scores: list[int] = []
    conversation_count = 0
    selected_activity_count = 0
    media_log_count = 0

    if session_ids:
        recommendations = (
            db.query(RecommendationRequest)
            .filter(RecommendationRequest.session_id.in_(session_ids))
            .all()
        )
        recommendation_count = len(recommendations)
        recommendation_ids = [item.id for item in recommendations]
        if recommendation_ids:
            activity_scores = [
                item.feedback_score
                for item in db.query(ActivityFeedback)
                .filter(ActivityFeedback.recommendation_id.in_(recommendation_ids))
                .all()
                if item.feedback_score is not None
            ]
            selected_activity_count = (
                db.query(ActivityFeedback)
                .filter(
                    ActivityFeedback.recommendation_id.in_(recommendation_ids),
                    ActivityFeedback.selected.is_(True),
                )
                .count()
            )
        media_logs = (
            db.query(MediaSelectionLog)
            .filter(MediaSelectionLog.session_id.in_(session_ids))
            .all()
        )
        media_log_count = len(media_logs)
        media_scores = [
            item.feedback_score
            for item in media_logs
            if item.feedback_score is not None
        ]
        conversation_count = (
            db.query(ConversationRequest)
            .filter(ConversationRequest.session_id.in_(session_ids))
            .count()
        )

    data_quality = (
        "enough_data" if len(sessions) >= MIN_SESSIONS_FOR_FULL_REPORT else "limited_data"
    )

    # Build emotion distribution
    label_counts: Counter = Counter(s.emotion_label for s in sessions)
    total = len(sessions) or 1
    emotion_distribution = {label: round(count / total, 3) for label, count in label_counts.items()}

    # Build TFT cards
    cards: list[dict] = []

    if data_quality == "limited_data":
        cards.append({
            "title": "Cần thêm dữ liệu",
            "body": f"Chỉ có {len(sessions)} phiên trong kỳ này. Hãy check-in thêm để xem báo cáo đầy đủ.",
            "severity": "warn",
            "action_id": "report:limited",
        })
        if sessions:
            cards.append({
                "title": "Phân bố hiện tại",
                "body": " | ".join(
                    f"{k.capitalize()} {round(v*100)}%" for k, v in emotion_distribution.items()
                ),
                "severity": "info",
                "action_id": "report:distribution",
            })
            cards.append(_trend_card(sessions))
    else:
        # Dominant emotion
        dominant = label_counts.most_common(1)[0] if label_counts else ("neutral", 0)
        cards.append({
            "title": "Cảm xúc chủ đạo",
            "body": f"{dominant[0].capitalize()} — {dominant[1]}/{len(sessions)} phiên ({round(dominant[1]/total*100)}%)",
            "severity": "info",
            "action_id": "report:dominant_emotion",
        })

        cards.append(_trend_card(sessions))

        # Distribution card
        dist_text = " | ".join(
            f"{k.capitalize()} {round(v*100)}%" for k, v in list(emotion_distribution.items())[:3]
        )
        cards.append({
            "title": "Phân bố cảm xúc",
            "body": dist_text,
            "severity": "info",
            "action_id": "report:distribution",
        })

        support_parts = [
            f"{recommendation_count} lượt gợi ý",
            f"{selected_activity_count} activity đã chọn",
            f"{media_log_count} media log",
            f"{conversation_count} hội thoại",
        ]
        activity_avg = _avg(activity_scores)
        media_avg = _avg(media_scores)
        if activity_avg is not None:
            support_parts.append(f"activity {activity_avg}/5")
        if media_avg is not None:
            support_parts.append(f"media {media_avg}/5")
        cards.append({
            "title": "Hiệu quả hỗ trợ",
            "body": " · ".join(support_parts),
            "severity": "info",
            "action_id": "report:support_effectiveness",
        })

    # Trend summary text
    trend_summary = None
    if sessions:
        negative_percent = round(_negative_ratio(sessions) * 100)
        trend_summary = (
            f"{len(sessions)} phiên trong kỳ này. "
            + (f"Cảm xúc chủ đạo: {label_counts.most_common(1)[0][0]}. " if label_counts else "")
            + f"Tỷ lệ cảm xúc cần hỗ trợ: {negative_percent}%."
        )

    report = TftReport(
        id=str(uuid.uuid4()),
        user_id=user_id,
        period_type=period_type,
        period_start=period_start,
        period_end=period_end,
        tft_cards=cards,
        emotion_distribution=emotion_distribution,
        trend_summary=trend_summary,
        data_quality=data_quality,
        generated_at=datetime.now(timezone.utc),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get(
    "/tft-summary",
    response_model=TftSummaryResponse,
    summary="Lấy report rút gọn theo period",
)
def get_tft_summary(
    period: str = Query(
        ...,
        description="daily | weekly | monthly | yearly",
    ),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    """
    Lấy TFT report gần nhất cho period yêu cầu.
    Nếu chưa có, tự generate ngay.
    """
    if period not in ("daily", "weekly", "monthly", "yearly"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="period must be one of: daily, weekly, monthly, yearly",
        )

    # Try to find existing report for this period
    period_start, _ = _period_bounds(period)
    existing = (
        db.query(TftReport)
        .filter(
            TftReport.user_id == current_device.user_id,
            TftReport.period_type == period,
            TftReport.period_start == period_start,
        )
        .order_by(TftReport.generated_at.desc())
        .first()
    )

    if existing:
        report = existing
    else:
        report = _generate_report(
            user_id=current_device.user_id,
            device_id=current_device.id,
            period_type=period,
            db=db,
        )

    return TftSummaryResponse(
        report_id=report.id,
        period_type=report.period_type,
        period_start=report.period_start,
        period_end=report.period_end,
        cards=report.tft_cards,
        emotion_distribution=report.emotion_distribution,
        trend_summary=report.trend_summary,
        data_quality=report.data_quality,
        generated_at=report.generated_at,
    )


@router.post(
    "/generate",
    response_model=ReportGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yêu cầu tạo report mới",
)
def generate_report(
    payload: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    """Tạo mới một TFT report cho period yêu cầu, luôn overwrite report cũ."""
    if payload.period_type not in ("daily", "weekly", "monthly", "yearly"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="period_type must be one of: daily, weekly, monthly, yearly",
        )

    report = _generate_report(
        user_id=current_device.user_id,
        device_id=current_device.id,
        period_type=payload.period_type,
        db=db,
    )

    return ReportGenerateResponse(
        report_id=report.id,
        period_type=report.period_type,
        data_quality=report.data_quality,
        cards=report.tft_cards,
        generated_at=report.generated_at,
    )


@router.get(
    "",
    summary="Liệt kê TFT reports gần nhất của thiết bị",
)
def list_reports(
    period_type: str | None = Query(default=None, description="daily | weekly | monthly | yearly"),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    query = db.query(TftReport).filter(TftReport.user_id == current_device.user_id)
    if period_type:
        if period_type not in ("daily", "weekly", "monthly", "yearly"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="period_type must be one of: daily, weekly, monthly, yearly",
            )
        query = query.filter(TftReport.period_type == period_type)
    reports = query.order_by(TftReport.generated_at.desc()).limit(limit).all()
    return {
        "items": [
            {
                "id": item.id,
                "period_type": item.period_type,
                "period_start": item.period_start,
                "period_end": item.period_end,
                "data_quality": item.data_quality,
                "trend_summary": item.trend_summary,
                "emotion_distribution": item.emotion_distribution,
                "cards": item.tft_cards,
                "generated_at": item.generated_at,
            }
            for item in reports
        ]
    }
