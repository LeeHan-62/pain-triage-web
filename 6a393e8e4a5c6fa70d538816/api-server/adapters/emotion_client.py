import os
from typing import Dict, Any
import httpx
from models.schemas import ConsultationInput


async def classify_emotion(data: ConsultationInput) -> Dict[str, Any]:
    api_url = os.getenv("KOBERT_EMOTION_API_URL", "")
    if not api_url:
        raise RuntimeError("未配置 KOBERT_EMOTION_API_URL")

    payload = {
        "text": data.description or " ".join([data.location, data.nature, data.duration, *data.symptoms]),
        "task": "pain_emotion_intensity",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()


def mock_emotion(data: ConsultationInput) -> Dict[str, Any]:
    text = f"{data.description}{data.nature}{' '.join(data.symptoms)}"
    score = 0.35
    if any(word in text for word in ["剧烈", "撕裂", "刀割", "大汗", "呕血"]):
        score = 0.9
    elif any(word in text for word in ["持续", "发热", "头晕", "麻木"]):
        score = 0.65

    if score >= 0.8:
        level = "重度痛苦"
    elif score >= 0.55:
        level = "中度痛苦"
    else:
        level = "轻度痛苦"

    return {
        "label": level,
        "score": score,
        "source": "mock",
    }
