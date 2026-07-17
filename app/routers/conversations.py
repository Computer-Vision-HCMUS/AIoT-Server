"""
Conversations router.

POST /api/conversations/respond — yêu cầu Cloud tạo phản hồi hỗ trợ cảm xúc
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_device
from app.database import get_db
from app.models.emoticare import ConversationRequest, Device, EmotionSession
from app.schemas import (
    ConversationHistoryResponse,
    ConversationRespondRequest,
    ConversationRespondResponse,
)
from app.services.conversation import (
    chat,
    detect_safety_flag,
    next_action as conversation_next_action,
    summarize_user_message,
)

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])

# Crisis keywords: nếu phát hiện thì escalate safety_flag = high.
CRISIS_KEYWORDS = [
    "tự tử", "tu tu", "tự làm hại", "tu lam hai", "muốn chết", "muon chet",
    "không muốn sống", "khong muon song", "suicide", "self-harm",
    "want to die", "end my life", "kill myself",
]

MEDIUM_RISK_KEYWORDS = [
    "hoảng loạn", "hoang loan", "panic", "mất kiểm soát", "mat kiem soat",
    "không chịu nổi", "khong chiu noi", "tuyệt vọng", "tuyet vong",
]

LOW_RISK_KEYWORDS = [
    "căng thẳng", "cang thang", "stress", "lo lắng", "lo lang", "anxiety",
    "buồn", "buon", "mệt", "met", "giận", "gian",
]

# Mapping emotion → empathetic response templates (TFT-friendly, ≤ 120 chars)
RESPONSE_TEMPLATES: dict[str, list[str]] = {
    "stressed": [
        "Mình hiểu bạn đang chịu nhiều áp lực. Hãy dừng lại, hít thở sâu và cho mình nghỉ một chút nhé.",
        "Căng thẳng là dấu hiệu bạn đang cố gắng. Hãy tạm dừng và chăm sóc bản thân một chút.",
    ],
    "angry": [
        "Tức giận là cảm xúc bình thường. Thử đi bộ hoặc hít thở sâu để hạ nhiệt nhé.",
        "Mình ở đây với bạn. Hãy để cảm xúc qua đi, đừng hành động khi còn nóng.",
    ],
    "sad": [
        "Buồn thì cứ để buồn, không cần vội vượt qua. Mình ở đây lắng nghe bạn.",
        "Bạn không cần phải mạnh mẽ mọi lúc. Cho phép bản thân nghỉ ngơi và chữa lành.",
    ],
    "tired": [
        "Mệt mỏi là tín hiệu cơ thể cần nghỉ. Hãy dừng lại và nạp lại năng lượng nhé.",
        "Bạn đã làm việc đủ rồi. Một giấc ngủ ngắn hay nghỉ hoàn toàn sẽ giúp bạn rất nhiều.",
    ],
    "happy": [
        "Thật vui khi bạn đang cảm thấy tốt! Hãy lưu giữ khoảnh khắc tích cực này.",
        "Năng lượng tích cực của bạn thật quý giá. Chia sẻ nó với những người xung quanh nhé!",
    ],
    "neutral": [
        "Bình thường cũng là một trạng thái tốt. Bạn có muốn làm điều gì để ngày hôm nay thêm ý nghĩa không?",
        "Cảm ơn bạn đã check-in. Mình luôn ở đây nếu bạn cần chia sẻ.",
    ],
    "uncertain": [
        "Không chắc cảm xúc thì cũng ổn. Hãy dừng lại và lắng nghe cơ thể mình nhé.",
        "Đôi khi khó gọi tên cảm xúc. Hít thở chậm và cho mình thêm một chút thời gian.",
    ],
}

CRISIS_RESPONSE = (
    "Mình lo cho bạn. Hãy liên hệ người thân, chuyên gia tâm lý hoặc đường dây hỗ trợ "
    "sức khỏe tâm thần ngay nhé. Bạn không đơn độc."
)

MEDIUM_RISK_RESPONSE = (
    "Mình nghe thấy bạn đang rất quá tải. Hãy tạm dừng, ở cạnh một người tin cậy "
    "và chọn một việc nhỏ an toàn ngay lúc này nhé."
)


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _detect_safety_flag(text: str) -> str:
    """Keyword-based safety check. Returns high | medium | low | none."""
    lower = text.lower()
    if _contains_any(lower, CRISIS_KEYWORDS):
        return "high"
    if _contains_any(lower, MEDIUM_RISK_KEYWORDS):
        return "medium"
    if _contains_any(lower, LOW_RISK_KEYWORDS):
        return "low"
    return "none"


def _next_action(emotion_label: str, safety_flag: str) -> str:
    if safety_flag == "high":
        return "contact_support"
    if safety_flag == "medium":
        return "grounding"
    if emotion_label in ("stressed", "angry"):
        return "breathing"
    if emotion_label in ("sad", "tired"):
        return "rest"
    return "reflect"


def _get_response(emotion_label: str, safety_flag: str, message: str | None) -> str:
    if safety_flag == "high":
        return CRISIS_RESPONSE
    if safety_flag == "medium":
        return MEDIUM_RISK_RESPONSE
    templates = RESPONSE_TEMPLATES.get(emotion_label, RESPONSE_TEMPLATES["neutral"])
    base = templates[0]
    if message and safety_flag == "low":
        return f"{base} Mình sẽ giữ phản hồi ngắn để bạn dễ đọc trên TFT."
    return base


def _summarize_user_message(message: str | None, safety_flag: str) -> str | None:
    if not message:
        return None
    if safety_flag == "high":
        return "[high_safety_signal_redacted]"
    return message[:200]


@router.post(
    "/respond",
    response_model=ConversationRespondResponse,
    status_code=status.HTTP_200_OK,
    summary="Yêu cầu Cloud tạo phản hồi hỗ trợ cảm xúc",
)
def respond(
    payload: ConversationRespondRequest,
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    """
    Nhận user_message và emotion context.
    Áp dụng safety filter, trả về 1 response card rút gọn cho TFT.
    """
    # Verify session
    session = (
        db.query(EmotionSession)
        .filter(
            EmotionSession.id == payload.session_id,
            EmotionSession.device_id == current_device.id,
        )
        .first()
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emotion session not found",
        )

    # Safety filter
    safety_flag = detect_safety_flag(payload.user_message or "")

    # Generate response
    try:
        response_text = chat(session.emotion_label, payload.user_message, safety_flag)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Live AI response is temporarily unavailable. Check the selected AI provider configuration and retry.",
        ) from exc
    next_action = conversation_next_action(session.emotion_label, safety_flag)

    # Text explicitly submitted to the companion is persisted as a short history item.
    # High-risk messages remain redacted by summarize_user_message.
    user_message_summary = summarize_user_message(payload.user_message, safety_flag)

    conversation = ConversationRequest(
        id=str(uuid.uuid4()),
        session_id=session.id,
        user_message_summary=user_message_summary,
        response_text=response_text,
        safety_flag=safety_flag,
        created_at=datetime.now(timezone.utc),
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    card = {
        "title": "Phản hồi hỗ trợ",
        "body": response_text,
        "severity": "alert" if safety_flag == "high" else ("warn" if safety_flag == "medium" else "info"),
        "next_action": next_action,
        "action_id": f"conversation:{conversation.id}",
    }

    return ConversationRespondResponse(
        conversation_id=conversation.id,
        safety_flag=safety_flag,
        card=card,
    )


@router.get("/history", response_model=ConversationHistoryResponse)
def conversation_history(
    session_id: str | None = Query(default=None, min_length=36, max_length=36),
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
    current_device: Device = Depends(get_current_device),
):
    """Load persisted assistant replies for sessions owned by this device."""
    query = (
        db.query(ConversationRequest)
        .join(ConversationRequest.session)
        .filter(EmotionSession.device_id == current_device.id)
    )
    if session_id:
        query = query.filter(ConversationRequest.session_id == session_id)

    conversations = query.order_by(ConversationRequest.created_at.desc()).limit(limit).all()
    return ConversationHistoryResponse(
        items=[
            {
                "id": item.id,
                "session_id": item.session_id,
                "user_message": item.user_message_summary,
                "response_text": item.response_text,
                "safety_flag": item.safety_flag,
                "created_at": item.created_at,
            }
            for item in reversed(conversations)
        ]
    )
