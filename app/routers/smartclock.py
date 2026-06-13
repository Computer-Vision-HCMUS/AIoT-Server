import re
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.auth import get_current_device
from app.database import get_db
from app.models.device import Device, SleepConfig, TimerConfig
from app.models.smartclock import (
    GameScore,
    PomodoroSession,
    PresentationSession,
    SleepQualityReport,
    SleepSensorBatch,
    SleepSession,
    StudySession,
)
from app.schemas import (
    GameScoreRequest,
    GameScoreResponse,
    PomodoroSessionRequest,
    PomodoroSessionResponse,
    PresentationSessionEndRequest,
    PresentationSessionResponse,
    PresentationSessionStartRequest,
    SleepConfigRequest,
    SleepConfigResponse,
    SleepFactorAnalysis,
    SleepMonthlySummaryResponse,
    SleepQualityReportRequest,
    SleepQualityReportResponse,
    SleepSensorBatchRequest,
    SleepSensorBatchResponse,
    SleepSessionDetailResponse,
    SleepSessionEndRequest,
    SleepSessionResponse,
    SleepSessionStartRequest,
    StudySessionCreateRequest,
    StudySessionResponse,
    StudySummaryResponse,
    TimerConfigRequest,
    TimerConfigResponse,
)

router = APIRouter(prefix="/smartclock", tags=["SmartClock"])

_MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def require_smartclock(device: Device) -> None:
    if device.device_type != "smartclock":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SmartClock device token required",
        )


def _validate_month(month: str) -> None:
    """Raise HTTP 422 if month is not in YYYY-MM format."""
    if not _MONTH_RE.match(month):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="month must be in YYYY-MM format",
        )


# ─── Timer Config ──────────────────────────────────────────────────────────────

@router.get("/timer-config", response_model=TimerConfigResponse)
def get_timer_config(
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    config = current_device.timer_config
    if config is None:
        config = TimerConfig(device_id=current_device.id)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.put("/timer-config", response_model=TimerConfigResponse)
def update_timer_config(
    payload: TimerConfigRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    config = current_device.timer_config
    if config is None:
        config = TimerConfig(device_id=current_device.id)
        db.add(config)
    config.study_duration = payload.study_duration
    config.break_duration = payload.break_duration
    db.commit()
    db.refresh(config)
    return config


# ─── Sleep Config ─────────────────────────────────────────────────────────────

@router.get("/sleep-config", response_model=SleepConfigResponse)
def get_sleep_config(
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    config = current_device.sleep_config
    if config is None:
        config = SleepConfig(device_id=current_device.id)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.put("/sleep-config", response_model=SleepConfigResponse)
def update_sleep_config(
    payload: SleepConfigRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    config = current_device.sleep_config
    if config is None:
        config = SleepConfig(device_id=current_device.id)
        db.add(config)
    config.alarm_enabled = payload.alarm_enabled
    config.alarm_time = payload.alarm_time if payload.alarm_enabled else None
    config.sleep_duration = payload.sleep_duration
    db.commit()
    db.refresh(config)
    return config


# ─── Pomodoro Sessions ────────────────────────────────────────────────────────

@router.post(
    "/pomodoro-sessions",
    response_model=PomodoroSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_pomodoro_session(
    payload: PomodoroSessionRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    session = PomodoroSession(device_id=current_device.id, **payload.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/pomodoro-sessions", response_model=list[PomodoroSessionResponse])
def list_pomodoro_sessions(
    from_date: Optional[datetime] = Query(default=None, description="Filter sessions from this datetime (inclusive)"),
    to_date: Optional[datetime] = Query(default=None, description="Filter sessions up to this datetime (inclusive)"),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)

    query = db.query(PomodoroSession).filter(PomodoroSession.device_id == current_device.id)

    if from_date is not None:
        query = query.filter(PomodoroSession.timestamp >= from_date)
    if to_date is not None:
        query = query.filter(PomodoroSession.timestamp <= to_date)

    return query.order_by(PomodoroSession.timestamp.desc()).all()


# ─── Game Scores ──────────────────────────────────────────────────────────────

@router.post(
    "/game-scores",
    response_model=GameScoreResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_game_score(
    payload: GameScoreRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    score = GameScore(device_id=current_device.id, **payload.model_dump())
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


# ─── Sleep Sessions ───────────────────────────────────────────────────────────

@router.post(
    "/sleep-sessions",
    response_model=SleepSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_sleep_session(
    payload: SleepSessionStartRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    session = SleepSession(device_id=current_device.id, start_time=payload.start_time)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


# Task 5.1 — GET /smartclock/sleep-sessions
@router.get("/sleep-sessions", response_model=list[SleepSessionResponse])
def list_sleep_sessions(
    month: Optional[str] = Query(default=None, description="Filter by month (YYYY-MM)"),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)

    if month is not None:
        _validate_month(month)

    query = db.query(SleepSession).filter(SleepSession.device_id == current_device.id)

    if month is not None:
        year_int, month_int = int(month[:4]), int(month[5:7])
        # Start of month
        start_of_month = datetime(year_int, month_int, 1, tzinfo=timezone.utc)
        # Start of next month
        if month_int == 12:
            start_of_next_month = datetime(year_int + 1, 1, 1, tzinfo=timezone.utc)
        else:
            start_of_next_month = datetime(year_int, month_int + 1, 1, tzinfo=timezone.utc)
        query = query.filter(
            SleepSession.start_time >= start_of_month,
            SleepSession.start_time < start_of_next_month,
        )

    sessions = query.order_by(SleepSession.start_time.desc()).all()
    return sessions


# Task 5.3 — GET /smartclock/sleep-sessions/summary
# MUST be registered BEFORE /sleep-sessions/{session_id}
@router.get("/sleep-sessions/summary", response_model=SleepMonthlySummaryResponse)
def get_sleep_sessions_summary(
    month: str = Query(..., description="Month in YYYY-MM format"),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    _validate_month(month)

    year_int, month_int = int(month[:4]), int(month[5:7])
    start_of_month = datetime(year_int, month_int, 1, tzinfo=timezone.utc)
    if month_int == 12:
        start_of_next_month = datetime(year_int + 1, 1, 1, tzinfo=timezone.utc)
    else:
        start_of_next_month = datetime(year_int, month_int + 1, 1, tzinfo=timezone.utc)

    # Query completed sessions in the month
    completed_sessions = (
        db.query(SleepSession)
        .filter(
            SleepSession.device_id == current_device.id,
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

    # Compute avg_sleep_score from sessions that have a sleep_score
    scores = [s.sleep_score for s in completed_sessions if s.sleep_score is not None]
    avg_sleep_score = sum(scores) / len(scores) if scores else None

    # Gather quality reports for completed sessions
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


# Task 5.2 — GET /smartclock/sleep-sessions/{session_id}
# Registered AFTER /sleep-sessions/summary to avoid route conflict
@router.get("/sleep-sessions/{session_id}", response_model=SleepSessionDetailResponse)
def get_sleep_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    session = (
        db.query(SleepSession)
        .options(selectinload(SleepSession.quality_report))
        .filter(
            SleepSession.id == session_id,
            SleepSession.device_id == current_device.id,
        )
        .first()
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.post("/sleep-sessions/{session_id}/end", response_model=SleepSessionResponse)
def end_sleep_session(
    session_id: int,
    payload: SleepSessionEndRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    session = (
        db.query(SleepSession)
        .filter(
            SleepSession.id == session_id,
            SleepSession.device_id == current_device.id,
        )
        .first()
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sleep session is not active",
        )
    if _ensure_tz(payload.end_time) <= _ensure_tz(session.start_time):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_time must be after start_time",
        )
    session.end_time = payload.end_time
    session.sleep_score = payload.sleep_score
    session.status = "completed"
    db.commit()
    db.refresh(session)
    return session


@router.post(
    "/sleep-sessions/{session_id}/sensor-batches",
    response_model=SleepSensorBatchResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sleep_sensor_batch(
    session_id: int,
    payload: SleepSensorBatchRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    sleep_session = (
        db.query(SleepSession)
        .filter(
            SleepSession.id == session_id,
            SleepSession.device_id == current_device.id,
        )
        .first()
    )
    if sleep_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if sleep_session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sleep session is not active",
        )
    batch = SleepSensorBatch(sleep_session_id=session_id, **payload.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


@router.get(
    "/sleep-sessions/{session_id}/quality-report",
    response_model=SleepQualityReportResponse,
)
def get_sleep_quality_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    report = (
        db.query(SleepQualityReport)
        .join(SleepSession)
        .filter(
            SleepSession.id == session_id,
            SleepSession.device_id == current_device.id,
        )
        .first()
    )
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report


@router.put(
    "/sleep-sessions/{session_id}/quality-report",
    response_model=SleepQualityReportResponse,
)
def upsert_sleep_quality_report(
    session_id: int,
    payload: SleepQualityReportRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    session = (
        db.query(SleepSession)
        .filter(
            SleepSession.id == session_id,
            SleepSession.device_id == current_device.id,
        )
        .first()
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    report = session.quality_report
    if report is None:
        report = SleepQualityReport(sleep_session_id=session.id)
        db.add(report)

    for field, value in payload.model_dump().items():
        setattr(report, field, value)

    db.commit()
    db.refresh(report)
    return report


# ─── Study Sessions ───────────────────────────────────────────────────────────

# Task 6.1 — POST /smartclock/study-sessions
@router.post(
    "/study-sessions",
    response_model=StudySessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_study_session(
    payload: StudySessionCreateRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)

    if payload.end_time <= payload.start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_time must be after start_time",
        )

    # Fetch the requested pomodoro sessions that belong to this device
    requested_ids = payload.pomodoro_session_ids
    pomodoro_sessions: list[PomodoroSession] = []

    if requested_ids:
        pomodoro_sessions = (
            db.query(PomodoroSession)
            .filter(
                PomodoroSession.id.in_(requested_ids),
                PomodoroSession.device_id == current_device.id,
            )
            .all()
        )

    found_ids = {ps.id for ps in pomodoro_sessions}
    invalid_ids = [pid for pid in requested_ids if pid not in found_ids]

    if invalid_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"IDs {invalid_ids} do not exist or do not belong to this device",
        )

    # Compute aggregates (duration is already stored in minutes)
    focus_minutes = sum(ps.duration for ps in pomodoro_sessions if ps.session_type == "study")
    break_minutes = sum(ps.duration for ps in pomodoro_sessions if ps.session_type == "break")
    pomodoro_count = sum(1 for ps in pomodoro_sessions if ps.session_type == "study")

    study_session = StudySession(
        device_id=current_device.id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        status=payload.status,
        focus_minutes=focus_minutes,
        break_minutes=break_minutes,
        pomodoro_count=pomodoro_count,
    )
    db.add(study_session)
    db.commit()
    db.refresh(study_session)
    return study_session


# Task 6.3 — GET /smartclock/study-sessions
@router.get("/study-sessions", response_model=list[StudySessionResponse])
def list_study_sessions(
    from_date: Optional[datetime] = Query(default=None, description="Filter sessions from this datetime (inclusive)"),
    to_date: Optional[datetime] = Query(default=None, description="Filter sessions up to this datetime (inclusive)"),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)

    query = db.query(StudySession).filter(StudySession.device_id == current_device.id)

    if from_date is not None:
        query = query.filter(StudySession.start_time >= from_date)
    if to_date is not None:
        query = query.filter(StudySession.start_time <= to_date)

    sessions = query.order_by(StudySession.start_time.desc()).all()
    return sessions


# Task 6.6 — GET /smartclock/study-sessions/summary
# MUST be registered BEFORE any /study-sessions/{id} route
@router.get("/study-sessions/summary", response_model=StudySummaryResponse)
def get_study_sessions_summary(
    period: str = Query(..., description="Aggregation period: day | week | month"),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)

    if period not in ("day", "week", "month"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="period must be one of: day, week, month",
        )

    now = datetime.now(timezone.utc)

    # Build time windows using Python datetime (portable across SQLite & PostgreSQL)
    if period == "day":
        # 7 most recent days (today inclusive)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        windows: list[tuple[datetime, datetime, str]] = []
        for i in range(6, -1, -1):
            day_start = today - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            key = day_start.strftime("%Y-%m-%d")
            windows.append((day_start, day_end, key))
        key_name = "date"

    elif period == "week":
        # 4 most recent weeks — each week starts on Monday
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # Start of the current week (Monday)
        current_week_start = today - timedelta(days=today.weekday())
        windows = []
        for i in range(3, -1, -1):
            week_start = current_week_start - timedelta(weeks=i)
            week_end = week_start + timedelta(weeks=1)
            key = week_start.strftime("%Y-%m-%d")
            windows.append((week_start, week_end, key))
        key_name = "week_start"

    else:  # month
        # 3 most recent months
        windows = []
        year, month_num = now.year, now.month
        for i in range(2, -1, -1):
            # Go back i months from current
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
            key = month_start.strftime("%Y-%m")
            windows.append((month_start, month_end, key))
        key_name = "month"

    # Fetch all study sessions within the full range
    range_start = windows[0][0]
    range_end = windows[-1][1]

    all_sessions = (
        db.query(StudySession)
        .filter(
            StudySession.device_id == current_device.id,
            StudySession.start_time >= range_start,
            StudySession.start_time < range_end,
        )
        .all()
    )

    # Aggregate into windows
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


def _ensure_tz(dt: datetime) -> datetime:
    """Return a timezone-aware datetime; assume UTC if naive (SQLite compatibility)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


# ─── Presentation Sessions ────────────────────────────────────────────────────

# Task 7.1 — POST /smartclock/presentation-sessions
@router.post(
    "/presentation-sessions",
    response_model=PresentationSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_presentation_session(
    payload: PresentationSessionStartRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    session = PresentationSession(
        device_id=current_device.id,
        start_time=payload.start_time,
        status="pending",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


# Task 7.2 — POST /smartclock/presentation-sessions/{session_id}/end
@router.post(
    "/presentation-sessions/{session_id}/end",
    response_model=PresentationSessionResponse,
)
def end_presentation_session(
    session_id: int,
    payload: PresentationSessionEndRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)

    session = (
        db.query(PresentationSession)
        .filter(
            PresentationSession.id == session_id,
            PresentationSession.device_id == current_device.id,
        )
        .first()
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if _ensure_tz(payload.end_time) <= _ensure_tz(session.start_time):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_time must be after start_time",
        )

    session.end_time = payload.end_time
    session.clarity_score = payload.clarity_score
    session.speed_score = payload.speed_score
    session.noise_score = payload.noise_score
    session.confidence_score = payload.confidence_score
    if payload.speech_rate is not None:
        session.speech_rate = payload.speech_rate
    if payload.feedback is not None:
        session.feedback = payload.feedback

    try:
        session.presentation_score = (
            payload.clarity_score
            + payload.speed_score
            + payload.noise_score
            + payload.confidence_score
        ) / 4
        session.status = "completed"
        db.commit()
        db.refresh(session)
    except Exception as e:
        session.status = "failed"
        session.error_message = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Score computation failed",
        )

    return session


# Task 7.4 — GET /smartclock/presentation-sessions
@router.get("/presentation-sessions", response_model=list[PresentationSessionResponse])
def list_presentation_sessions(
    from_date: Optional[datetime] = Query(default=None, description="Filter sessions from this datetime (inclusive)"),
    to_date: Optional[datetime] = Query(default=None, description="Filter sessions up to this datetime (inclusive)"),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)

    query = db.query(PresentationSession).filter(
        PresentationSession.device_id == current_device.id
    )

    if from_date is not None:
        query = query.filter(PresentationSession.start_time >= from_date)
    if to_date is not None:
        query = query.filter(PresentationSession.start_time <= to_date)

    sessions = query.order_by(PresentationSession.start_time.desc()).all()
    return sessions


# Task 7.7 — GET /smartclock/presentation-sessions/{session_id}
@router.get(
    "/presentation-sessions/{session_id}",
    response_model=PresentationSessionResponse,
)
def get_presentation_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    require_smartclock(current_device)
    session = (
        db.query(PresentationSession)
        .filter(
            PresentationSession.id == session_id,
            PresentationSession.device_id == current_device.id,
        )
        .first()
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session
