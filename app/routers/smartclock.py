from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_device
from app.database import get_db
from app.models.device import Device, SleepConfig, TimerConfig
from app.models.smartclock import (
    GameScore,
    PomodoroSession,
    SleepQualityReport,
    SleepSensorBatch,
    SleepSession,
)
from app.schemas import (
    GameScoreRequest,
    GameScoreResponse,
    PomodoroSessionRequest,
    PomodoroSessionResponse,
    SleepConfigRequest,
    SleepConfigResponse,
    SleepQualityReportRequest,
    SleepQualityReportResponse,
    SleepSensorBatchRequest,
    SleepSensorBatchResponse,
    SleepSessionEndRequest,
    SleepSessionResponse,
    SleepSessionStartRequest,
    TimerConfigRequest,
    TimerConfigResponse,
)

router = APIRouter(prefix="/smartclock", tags=["SmartClock"])


def require_smartclock(device: Device) -> None:
    if device.device_type != "smartclock":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SmartClock device token required",
        )


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
    session_exists = (
        db.query(SleepSession.id)
        .filter(
            SleepSession.id == session_id,
            SleepSession.device_id == current_device.id,
        )
        .first()
    )
    if session_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
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
