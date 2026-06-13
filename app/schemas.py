from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


DeviceType = Literal["smartclock", "visiondrive"]


class DeviceRegisterRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=64)
    device_type: DeviceType


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    device_type: DeviceType
    created_at: datetime
    last_seen_at: datetime


class DeviceRegisterResponse(DeviceResponse):
    device_token: str


class TimerConfigRequest(BaseModel):
    study_duration: int = Field(ge=1, le=120)
    break_duration: int = Field(gt=0, le=120)


class TimerConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    study_duration: int
    break_duration: int
    updated_at: datetime


class PomodoroSessionRequest(BaseModel):
    timestamp: datetime
    duration: int = Field(ge=1, le=1440)
    session_type: Literal["study", "break"]


class PomodoroSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    duration: int
    session_type: Literal["study", "break"]
    created_at: datetime


class GameScoreRequest(BaseModel):
    score: int = Field(ge=0)
    timestamp: datetime


class GameScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    score: int
    timestamp: datetime
    created_at: datetime


class SleepSessionStartRequest(BaseModel):
    start_time: datetime


class SleepSessionEndRequest(BaseModel):
    end_time: datetime
    sleep_score: float = Field(ge=0, le=100)


class SleepSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_time: datetime
    end_time: datetime | None
    status: Literal["active", "completed"]
    sleep_score: float | None


class SleepSensorBatchRequest(BaseModel):
    timestamp: datetime
    sound_level: float = Field(ge=0)
    light_level: float = Field(ge=0)


class SleepSensorBatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    sound_level: float
    light_level: float


class SleepQualityReportRequest(BaseModel):
    duration_minutes: float = Field(gt=0)
    quality_label: Literal["poor", "fair", "good", "excellent"]
    duration_score: float | None = Field(default=None, ge=0, le=100)
    sound_score: float | None = Field(default=None, ge=0, le=100)
    light_score: float | None = Field(default=None, ge=0, le=100)
    avg_sound_level: float | None = Field(default=None, ge=0)
    avg_light_level: float | None = Field(default=None, ge=0)
    duration_issue: bool = False
    noise_issue: bool = False
    light_issue: bool = False
    recommendation: str | None = Field(default=None, max_length=1000)


class SleepQualityReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sleep_session_id: int
    duration_minutes: float
    quality_label: Literal["poor", "fair", "good", "excellent"]
    duration_score: float | None
    sound_score: float | None
    light_score: float | None
    avg_sound_level: float | None
    avg_light_level: float | None
    duration_issue: bool
    noise_issue: bool
    light_issue: bool
    recommendation: str | None
    generated_at: datetime


class TripStartRequest(BaseModel):
    start_time: datetime


class TripEndRequest(BaseModel):
    end_time: datetime
    safety_score: float = Field(ge=0, le=100)


class TripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_time: datetime
    end_time: datetime | None
    status: Literal["active", "completed"]
    safety_score: float | None


class DistractionEventRequest(BaseModel):
    timestamp: datetime
    event_type: Literal["drowsiness", "gaze_distraction", "phone_use"]
    severity: Literal["low", "medium", "high"]


class DistractionEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    event_type: Literal["drowsiness", "gaze_distraction", "phone_use"]
    severity: Literal["low", "medium", "high"]


class SleepConfigRequest(BaseModel):
    alarm_enabled: bool
    alarm_time: str | None = Field(default=None, max_length=5)
    sleep_duration: int = Field(ge=30, le=720)

    @field_validator("alarm_time")
    @classmethod
    def validate_alarm_time(cls, value: str | None) -> str | None:
        if value is None:
            return value
        hour, separator, minute = value.partition(":")
        if separator != ":" or not hour.isdigit() or not minute.isdigit():
            raise ValueError("alarm_time must use HH:MM format")
        if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
            raise ValueError("alarm_time must use HH:MM format")
        return value


class SleepConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    alarm_enabled: bool
    alarm_time: str | None
    sleep_duration: int
    updated_at: datetime


class StudySessionCreateRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    status: Literal["completed", "interrupted"]
    pomodoro_session_ids: list[int]


class StudySessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_time: datetime
    end_time: datetime
    status: Literal["completed", "interrupted"]
    focus_minutes: float
    break_minutes: float
    pomodoro_count: int
    created_at: datetime


class StudySummaryResponse(BaseModel):
    total_focus_minutes: float
    total_pomodoro_count: int
    data_points: list[dict]  # keys vary by period: date / week_start / month


# ── Sleep Session GET schemas ──────────────────────────────────────────────────

class SleepFactorAnalysis(BaseModel):
    noise_issue_count: int
    light_issue_count: int
    duration_issue_count: int


class SleepMonthlySummaryResponse(BaseModel):
    avg_sleep_score: float | None
    avg_duration_minutes: float | None
    total_sessions: int
    factor_analysis: SleepFactorAnalysis


class SleepSessionDetailResponse(SleepSessionResponse):
    model_config = ConfigDict(from_attributes=True)

    quality_report: SleepQualityReportResponse | None


# ── Presentation Session schemas ───────────────────────────────────────────────

class PresentationSessionStartRequest(BaseModel):
    start_time: datetime


class PresentationSessionEndRequest(BaseModel):
    end_time: datetime
    clarity_score: float = Field(ge=0, le=100)
    speed_score: float = Field(ge=0, le=100)
    noise_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    speech_rate: float | None = Field(default=None, ge=0, le=1000)
    feedback: str | None = Field(default=None, max_length=1000)


class PresentationSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_time: datetime
    end_time: datetime | None
    status: Literal["pending", "processing", "completed", "failed"]
    presentation_score: float | None
    clarity_score: float | None
    speed_score: float | None
    noise_score: float | None
    confidence_score: float | None
    speech_rate: float | None
    feedback: str | None
    error_message: str | None
    created_at: datetime


# ── Dashboard schemas ──────────────────────────────────────────────────────────

class DashboardOverviewResponse(BaseModel):
    study_sessions_count: int
    total_pomodoro_count: int
    sleep_sessions_count: int
    avg_sleep_score: float | None
    presentation_sessions_count: int
    avg_presentation_score: float | None


class DashboardPresentationPoint(BaseModel):
    session_id: int
    start_time: datetime
    presentation_score: float
