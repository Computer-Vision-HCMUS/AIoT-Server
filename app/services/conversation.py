"""Safety-first conversation policy for the EmotiCare companion.

This module is deliberately deterministic around crisis handling. High and
medium-risk messages never reach an LLM, and every generated response is
checked again before it is returned or persisted.
"""

import re
import unicodedata


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    ascii_text = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", ascii_text.replace("đ", "d")).strip()


HIGH_RISK_PATTERNS = (
    r"\b(tu tu|tu lam hai|muon chet|khong muon song|ket thuc cuoc doi)\b",
    r"\b(giet minh|lam hai ban than|cat tay|uong thuoc qua lieu)\b",
    r"\b(suicide|self harm|want to die|end my life|kill myself|hurt myself)\b",
    r"\b(have a plan|goodbye forever|better off without me)\b",
)

MEDIUM_RISK_PATTERNS = (
    r"\b(hoang loan|mat kiem soat|khong chiu noi|tuyet vong|vo vong)\b",
    r"\b(panic|losing control|cannot cope|cant cope|hopeless)\b",
)

LOW_RISK_PATTERNS = (
    r"\b(cang thang|lo lang|buon|met|gian|so hai|co don)\b",
    r"\b(stress|anxiety|anxious|sad|tired|angry|afraid|lonely)\b",
)

# Output patterns are intentionally conservative. If an LLM crosses one of
# these boundaries, the response is replaced by a known-safe template.
UNSAFE_OUTPUT_PATTERNS = (
    # Diagnosis / medical certainty
    r"\b(ban (bi|mac|chac chan bi)|toi chan doan|you (have|definitely have)|diagnos)\b",
    # Medication or treatment instructions
    r"\b(uong|dung|ngung|tang|giam)\s+\d+\s*(mg|vien|ml)\b",
    r"\b(stop taking|double the dose|increase the dose|decrease the dose)\b",
    # Judgement, blame, coercion
    r"\b(do loi cua ban|ban yeu duoi|ban that te|you are weak|your fault|pathetic)\b",
    # Dangerous encouragement
    r"\b(hay tu lam hai|cu tu tu|lam dieu nguy hiem|hurt yourself|kill yourself)\b",
)

RESPONSE_TEMPLATES = {
    "stressed": "Mình nghe thấy bạn đang chịu áp lực. Thử đặt chân vững trên sàn và thở chậm trong một phút nhé.",
    "angry": "Cảm giác tức giận có thể rất mạnh. Hãy tạm rời tình huống và thở chậm trước khi quyết định điều gì nhé.",
    "sad": "Mình nghe thấy nỗi buồn của bạn. Bạn có thể chọn một người tin cậy để chia sẻ một điều nhỏ lúc này.",
    "tired": "Có vẻ bạn đang mệt. Hãy cho mình một khoảng nghỉ ngắn và kiểm tra nhu cầu cơ bản như nước, thức ăn hoặc giấc ngủ nhé.",
    "happy": "Thật vui khi bạn đang có cảm xúc tích cực. Bạn có thể ghi lại điều đã giúp hôm nay trở nên tốt hơn.",
    "neutral": "Cảm ơn bạn đã chia sẻ. Bạn muốn dành một phút để nhận biết điều mình cần nhất lúc này không?",
    "uncertain": "Khó gọi tên cảm xúc cũng không sao. Hãy thở chậm và chú ý một cảm giác trong cơ thể lúc này nhé.",
}

CRISIS_RESPONSE = (
    "Mình rất lo cho sự an toàn của bạn. Hãy ở cạnh một người bạn tin cậy và nói rõ rằng bạn cần hỗ trợ ngay. "
    "Hãy liên hệ chuyên gia sức khỏe tâm thần hoặc dịch vụ hỗ trợ khẩn cấp tại nơi bạn sống; "
    "nếu có nguy hiểm trước mắt, hãy gọi dịch vụ cấp cứu địa phương ngay."
)

MEDIUM_RISK_RESPONSE = (
    "Mình nghe thấy bạn đang rất quá tải. Hãy đến một nơi an toàn, ở cạnh người bạn tin cậy và liên hệ "
    "chuyên gia hoặc dịch vụ hỗ trợ phù hợp nếu cảm giác này tiếp tục tăng lên."
)


def _matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def detect_safety_flag(text: str) -> str:
    normalized = _normalize(text)
    if _matches_any(normalized, HIGH_RISK_PATTERNS):
        return "high"
    if _matches_any(normalized, MEDIUM_RISK_PATTERNS):
        return "medium"
    if _matches_any(normalized, LOW_RISK_PATTERNS):
        return "low"
    return "none"


def next_action(emotion_label: str, safety_flag: str) -> str:
    if safety_flag == "high":
        return "contact_support"
    if safety_flag == "medium":
        return "seek_support"
    if emotion_label in ("stressed", "angry"):
        return "breathing"
    if emotion_label in ("sad", "tired"):
        return "rest"
    return "reflect"


def fallback_response(emotion_label: str, safety_flag: str, message: str | None) -> str:
    if safety_flag == "high":
        return CRISIS_RESPONSE
    if safety_flag == "medium":
        return MEDIUM_RISK_RESPONSE
    return RESPONSE_TEMPLATES.get(emotion_label, RESPONSE_TEMPLATES["neutral"])


def summarize_user_message(message: str | None, safety_flag: str) -> str | None:
    if not message:
        return None
    if safety_flag in ("high", "medium"):
        return f"[{safety_flag}_safety_signal_redacted]"
    return message[:200]


def _looks_like_unreliable_transcript(message: str | None) -> bool:
    if not message:
        return False
    words = re.findall(r"\w+", message.lower(), flags=re.UNICODE)
    if len(words) < 12:
        return False
    return len(words) > 100 or len(set(words)) / len(words) < 0.38


def is_safe_response(response: str) -> bool:
    normalized = _normalize(response)
    return bool(normalized) and not _matches_any(normalized, UNSAFE_OUTPUT_PATTERNS)


def chat(emotion_label: str, user_message: str | None, safety_flag: str) -> str:
    fallback = fallback_response(emotion_label, safety_flag, user_message)
    # Crisis and significant distress use deterministic policy text only.
    if safety_flag in ("high", "medium"):
        return fallback
    if _looks_like_unreliable_transcript(user_message):
        return (
            "Mình chưa chắc đã nghe đúng đoạn ghi âm. Bạn thử nói lại một câu ngắn, "
            "hoặc gửi bằng chữ để mình phản hồi sát hơn nhé."
        )

    from app.services.gemini import gemini_client

    prompt = (
        "Bạn là trợ lý hỗ trợ cảm xúc EmotiCare, không phải bác sĩ và không thay thế hỗ trợ chuyên môn. "
        "Trả lời bằng tiếng Việt trong 2-3 câu ngắn, ấm áp, trung lập và không phán xét. "
        "Không chẩn đoán bệnh, không khẳng định tình trạng y khoa, không hướng dẫn thuốc hoặc điều trị, "
        "không đổ lỗi, không khuyến khích hành vi nguy hiểm. Chỉ đề xuất một bước nhỏ, ít rủi ro. "
        f"Cảm xúc nhận diện: {emotion_label}. Người dùng nói: {user_message or '[không có nội dung]'}"
    )
    response = gemini_client.generate_text(prompt, fallback=fallback, require_live=True)[:500]
    return response if is_safe_response(response) else fallback
