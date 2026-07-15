"""Statistic/report helpers used by TFT statistic aliases."""

from sqlalchemy.orm import Session

from app.models.emoticare import Device, TftReport


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
    if existing:
        return existing
    return _generate_report(
        user_id=current_device.user_id,
        device_id=current_device.id,
        period_type=period_type,
        db=db,
    )
