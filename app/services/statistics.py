"""Statistic/report helpers used by TFT statistic aliases."""

from sqlalchemy.orm import Session

from app.models.emoticare import Device, TftReport
from app.services.gemini import gemini_client


def build_statistics(period_type: str, current_device: Device, db: Session) -> TftReport:
    """Return the latest report for a period, generating one when needed."""
    from app.routers.reports import _generate_report, _period_bounds

    period_start, _ = _period_bounds(period_type)
    existing = (
        db.query(TftReport)
        .filter(
            TftReport.user_id == current_device.user_id,
            TftReport.period_type == period_type,
            TftReport.period_start == period_start,
        )
        .order_by(TftReport.generated_at.desc())
        .first()
    )
    # Statistics must reflect every newly-synced check-in. Rebuild the current
    # period instead of serving a stale report generated earlier in the day.
    if existing:
        db.delete(existing)
        db.commit()
    return _generate_report(
        user_id=current_device.user_id,
        device_id=current_device.id,
        period_type=period_type,
        db=db,
    )


def explain_statistics(report: TftReport) -> str:
    """Turn numeric report data into a concise, plain-Vietnamese explanation."""
    distribution = ", ".join(
        f"{label}: {round(float(value) * 100)}%"
        for label, value in report.emotion_distribution.items()
    ) or "chưa có dữ liệu"
    prompt = (
        "Bạn là EmotiCare, trợ lý giải thích báo cáo cảm xúc. "
        "Viết bằng tiếng Việt thật dễ hiểu, 2-3 câu ngắn. Không chẩn đoán y khoa, "
        "không khẳng định quá mức; nếu dữ liệu còn ít hãy nói rõ đây mới là tín hiệu ban đầu. "
        f"Kỳ báo cáo: {report.period_type}. Chất lượng dữ liệu: {report.data_quality}. "
        f"Phân bố cảm xúc: {distribution}. Xu hướng hệ thống: {report.trend_summary or 'chưa có'}."
    )
    return gemini_client.generate_text(prompt, fallback="", require_live=True)[:500]
