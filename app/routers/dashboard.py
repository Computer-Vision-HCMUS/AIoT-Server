import re
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.device import Device
from app.models.smartclock import (
    PresentationSession,
    SleepQualityReport,
    SleepSession,
    StudySession,
)
from app.schemas import (
    DashboardOverviewResponse,
    DashboardPresentationPoint,
    SleepFactorAnalysis,
    SleepMonthlySummaryResponse,
    StudySummaryResponse,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

_MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def _get_smartclock_device(device_id: int, db: Session) -> Device:
    """Query Device by id and device_type='smartclock'. Raise HTTP 404 if not found."""
    device = (
        db.query(Device)
        .filter(Device.id == device_id, Device.device_type == "smartclock")
        .first()
    )
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or is not a SmartClock",
        )
    return device


def _ensure_tz(dt: datetime) -> datetime:
    """Return a timezone-aware datetime; assume UTC if naive (SQLite compatibility)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


# ─── Task 9.2 — GET /dashboard/overview ──────────────────────────────────────

@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(
    device_id: int = Query(..., description="SmartClock device ID"),
    db: Session = Depends(get_db),
):
    _get_smartclock_device(device_id, db)

    cutoff = datetime.now(timezone.utc) - timedelta(days=30)

    # Study sessions in last 30 days
    study_sessions = (
        db.query(StudySession)
        .filter(
            StudySession.device_id == device_id,
            StudySession.start_time >= cutoff,
        )
        .all()
    )
    study_sessions_count = len(study_sessions)
    total_pomodoro_count = sum(s.pomodoro_count for s in study_sessions)

    # Sleep sessions in last 30 days
    sleep_sessions = (
        db.query(SleepSession)
        .filter(
            SleepSession.device_id == device_id,
            SleepSession.start_time >= cutoff,
        )
        .all()
    )
    sleep_sessions_count = len(sleep_sessions)
    completed_sleep_scores = [
        s.sleep_score
        for s in sleep_sessions
        if s.status == "completed" and s.sleep_score is not None
    ]
    avg_sleep_score = (
        sum(completed_sleep_scores) / len(completed_sleep_scores)
        if completed_sleep_scores
        else None
    )

    # Presentation sessions in last 30 days
    presentation_sessions = (
        db.query(PresentationSession)
        .filter(
            PresentationSession.device_id == device_id,
            PresentationSession.start_time >= cutoff,
        )
        .all()
    )
    presentation_sessions_count = len(presentation_sessions)
    completed_presentation_scores = [
        s.presentation_score
        for s in presentation_sessions
        if s.status == "completed" and s.presentation_score is not None
    ]
    avg_presentation_score = (
        sum(completed_presentation_scores) / len(completed_presentation_scores)
        if completed_presentation_scores
        else None
    )

    return DashboardOverviewResponse(
        study_sessions_count=study_sessions_count,
        total_pomodoro_count=total_pomodoro_count,
        sleep_sessions_count=sleep_sessions_count,
        avg_sleep_score=avg_sleep_score,
        presentation_sessions_count=presentation_sessions_count,
        avg_presentation_score=avg_presentation_score,
    )


# ─── Task 9.4 — GET /dashboard/study ─────────────────────────────────────────

@router.get("/study", response_model=StudySummaryResponse)
def get_dashboard_study(
    device_id: int = Query(..., description="SmartClock device ID"),
    period: str = Query(..., description="Aggregation period: day | week | month"),
    db: Session = Depends(get_db),
):
    _get_smartclock_device(device_id, db)

    if period not in ("day", "week", "month"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="period must be one of: day, week, month",
        )

    now = datetime.now(timezone.utc)

    if period == "day":
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        windows: list[tuple[datetime, datetime, str]] = []
        for i in range(6, -1, -1):
            day_start = today - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            windows.append((day_start, day_end, day_start.strftime("%Y-%m-%d")))
        key_name = "date"

    elif period == "week":
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        current_week_start = today - timedelta(days=today.weekday())
        windows = []
        for i in range(3, -1, -1):
            week_start = current_week_start - timedelta(weeks=i)
            week_end = week_start + timedelta(weeks=1)
            windows.append((week_start, week_end, week_start.strftime("%Y-%m-%d")))
        key_name = "week_start"

    else:  # month
        windows = []
        year, month_num = now.year, now.month
        for i in range(2, -1, -1):
            m = month_num - i
            y = year
            while m <= 0:
                m += 12
                y -= 1
            month_start = datetime(y, m, 1, tzinfo=timezone.utc)
            if m == 12:
                month_end = datetime(y + 1, 1, 1, tzinfo=timezone.utc)
            else:
                month_end = datetime(y, m + 1, 1, tzinfo=timezone.utc)
            windows.append((month_start, month_end, month_start.strftime("%Y-%m")))
        key_name = "month"

    range_start = windows[0][0]
    range_end = windows[-1][1]

    all_sessions = (
        db.query(StudySession)
        .filter(
            StudySession.device_id == device_id,
            StudySession.start_time >= range_start,
            StudySession.start_time < range_end,
        )
        .all()
    )

    data_points: list[dict] = []
    total_focus_minutes = 0.0
    total_pomodoro_count = 0

    for window_start, window_end, key_value in windows:
        window_sessions = [
            s for s in all_sessions
            if window_start <= _ensure_tz(s.start_time) < window_end
        ]
        focus = sum(s.focus_minutes for s in window_sessions)
        pomodoros = sum(s.pomodoro_count for s in window_sessions)
        total_focus_minutes += focus
        total_pomodoro_count += pomodoros
        data_points.append({
            key_name: key_value,
            "focus_minutes": focus,
            "pomodoro_count": pomodoros,
        })

    return StudySummaryResponse(
        total_focus_minutes=total_focus_minutes,
        total_pomodoro_count=total_pomodoro_count,
        data_points=data_points,
    )


# ─── Task 9.5 — GET /dashboard/sleep ─────────────────────────────────────────

@router.get("/sleep", response_model=SleepMonthlySummaryResponse)
def get_dashboard_sleep(
    device_id: int = Query(..., description="SmartClock device ID"),
    month: str = Query(..., description="Month in YYYY-MM format"),
    db: Session = Depends(get_db),
):
    _get_smartclock_device(device_id, db)

    if not _MONTH_RE.match(month):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="month must be in YYYY-MM format",
        )

    year_int, month_int = int(month[:4]), int(month[5:7])
    start_of_month = datetime(year_int, month_int, 1, tzinfo=timezone.utc)
    if month_int == 12:
        start_of_next_month = datetime(year_int + 1, 1, 1, tzinfo=timezone.utc)
    else:
        start_of_next_month = datetime(year_int, month_int + 1, 1, tzinfo=timezone.utc)

    completed_sessions = (
        db.query(SleepSession)
        .filter(
            SleepSession.device_id == device_id,
            SleepSession.status == "completed",
            SleepSession.start_time >= start_of_month,
            SleepSession.start_time < start_of_next_month,
        )
        .all()
    )

    total_sessions = len(completed_sessions)

    if total_sessions == 0:
        return SleepMonthlySummaryResponse(
            avg_sleep_score=None,
            avg_duration_minutes=None,
            total_sessions=0,
            factor_analysis=SleepFactorAnalysis(
                noise_issue_count=0,
                light_issue_count=0,
                duration_issue_count=0,
            ),
        )

    scores = [s.sleep_score for s in completed_sessions if s.sleep_score is not None]
    avg_sleep_score = sum(scores) / len(scores) if scores else None

    session_ids = [s.id for s in completed_sessions]
    reports = (
        db.query(SleepQualityReport)
        .filter(SleepQualityReport.sleep_session_id.in_(session_ids))
        .all()
    )

    durations = [r.duration_minutes for r in reports]
    avg_duration_minutes = sum(durations) / len(durations) if durations else None

    noise_issue_count = sum(1 for r in reports if r.noise_issue)
    light_issue_count = sum(1 for r in reports if r.light_issue)
    duration_issue_count = sum(1 for r in reports if r.duration_issue)

    return SleepMonthlySummaryResponse(
        avg_sleep_score=avg_sleep_score,
        avg_duration_minutes=avg_duration_minutes,
        total_sessions=total_sessions,
        factor_analysis=SleepFactorAnalysis(
            noise_issue_count=noise_issue_count,
            light_issue_count=light_issue_count,
            duration_issue_count=duration_issue_count,
        ),
    )


# ─── Task 9.6 — GET /dashboard/presentation ──────────────────────────────────

@router.get("/presentation", response_model=list[DashboardPresentationPoint])
def get_dashboard_presentation(
    device_id: int = Query(..., description="SmartClock device ID"),
    limit: int = Query(default=20, description="Number of results to return (1–100)"),
    db: Session = Depends(get_db),
):
    _get_smartclock_device(device_id, db)

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="limit must be between 1 and 100",
        )

    recent_sessions = (
        db.query(PresentationSession)
        .filter(
            PresentationSession.device_id == device_id,
            PresentationSession.status == "completed",
        )
        .order_by(PresentationSession.start_time.desc())
        .limit(limit)
        .all()
    )
    sessions = sorted(recent_sessions, key=lambda s: _ensure_tz(s.start_time))

    return [
        DashboardPresentationPoint(
            session_id=s.id,
            start_time=s.start_time,
            presentation_score=s.presentation_score,
        )
        for s in sessions
    ]
