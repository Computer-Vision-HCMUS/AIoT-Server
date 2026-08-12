"""Statistic aliases for day/week/month TFT reports."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_device
from app.database import get_db
from app.models.emoticare import Device
from app.schemas import StatisticsExplanationResponse, TftSummaryResponse
from app.services.statistics import build_statistics, explain_statistics

router = APIRouter(prefix="/api/statistics", tags=["Statistics"])


def _response_for_period(period_type: str, current_device: Device, db: Session) -> TftSummaryResponse:
    report = build_statistics(period_type, current_device, db)
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


@router.get("/day", response_model=TftSummaryResponse, summary="Daily emotion statistics")
def statistic_day(
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    return _response_for_period("daily", current_device, db)


@router.get("/week", response_model=TftSummaryResponse, summary="Weekly emotion statistics")
def statistic_week(
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    return _response_for_period("weekly", current_device, db)


@router.get("/month", response_model=TftSummaryResponse, summary="Monthly emotion statistics")
def statistic_month(
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    return _response_for_period("monthly", current_device, db)


@router.post("/{period}/explain", response_model=StatisticsExplanationResponse)
def explain_period_statistics(
    period: str,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    period_type = {"day": "daily", "week": "weekly", "month": "monthly"}.get(period)
    if period_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown statistics period")
    report = build_statistics(period_type, current_device, db)
    try:
        explanation = explain_statistics(report)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The selected AI provider is temporarily unavailable. Please retry.",
        ) from exc
    return StatisticsExplanationResponse(period_type=period_type, explanation=explanation)
