"""Conversation service with safety filtering and contextual AI responses."""

import re

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


def detect_safety_flag(text: str) -> str:
    lower = text.lower()
    if _contains_any(lower, CRISIS_KEYWORDS):
        return "high"
    if _contains_any(lower, MEDIUM_RISK_KEYWORDS):
        return "medium"
    if _contains_any(lower, LOW_RISK_KEYWORDS):
        return "low"
    return "none"


def next_action(emotion_label: str, safety_flag: str) -> str:
    if safety_flag == "high":
        return "contact_support"
    if safety_flag == "medium":
        return "grounding"
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
    templates = RESPONSE_TEMPLATES.get(emotion_label, RESPONSE_TEMPLATES["neutral"])
    base = templates[0]
    if message and safety_flag == "low":
        return f"{base} Mình sẽ giữ phản hồi ngắn để bạn dễ đọc trên TFT."
    return base


def summarize_user_message(message: str | None, safety_flag: str) -> str | None:
    if not message:
        return None
    if safety_flag == "high":
        return "[high_safety_signal_redacted]"
    return message[:200]


def _looks_like_unreliable_transcript(message: str | None) -> bool:
    """Detect long, highly repetitive STT output before sending it to the AI."""
    if not message:
        return False
    words = re.findall(r"\w+", message.lower(), flags=re.UNICODE)
    if len(words) < 12:
        return False
    unique_ratio = len(set(words)) / len(words)
    return len(words) > 100 or unique_ratio < 0.38


def chat(emotion_label: str, user_message: str | None, safety_flag: str) -> str:
    fallback = fallback_response(emotion_label, safety_flag, user_message)
    if safety_flag in ("high", "medium"):
        return fallback

    if _looks_like_unreliable_transcript(user_message):
        return (
            "Mình nhận được đoạn ghi âm khá dài hoặc bị lặp, nên chưa chắc đã hiểu đúng. "
            "Bạn thử nói lại một câu ngắn, hoặc gửi bằng chữ để mình phản hồi sát hơn nhé."
        )

    from app.services.gemini import gemini_client

    prompt = (
        "Reply in Vietnamese in 2-3 short, natural sentences. Mention one specific detail or feeling from "
        "the user's message, suggest exactly one small practical next step, and finish with one brief open question. "
        "Avoid generic reassurance, repeating the user's wording, medical diagnosis, and saying that you are AI. "
        "Bạn là trợ lý hỗ trợ cảm xúc cho thiết bị EmotiCare có màn hình TFT nhỏ. "
        "Trả lời bằng tiếng Việt, 1-2 câu, ấm áp, không chẩn đoán y khoa. "
        f"Cảm xúc nhận diện: {emotion_label}. "
        f"Người dùng nói: {user_message or '[không có nội dung]'}"
    )
    return gemini_client.generate_text(prompt, fallback=fallback, require_live=True)[:500]
