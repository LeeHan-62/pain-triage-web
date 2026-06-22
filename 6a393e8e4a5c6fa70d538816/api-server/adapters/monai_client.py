import os
from typing import Dict, Any
import httpx
from models.schemas import ConsultationInput


async def classify_with_monai(data: ConsultationInput, structured: Dict[str, Any]) -> Dict[str, Any]:
    api_url = os.getenv("MONAI_API_URL", "")
    if not api_url:
        raise RuntimeError("未配置 MONAI_API_URL")

    payload = {
        "text": data.description,
        "structured": structured,
        "task": "pain_triage_multiclass",
        "labels": {
            "location": ["头痛", "颈肩痛", "胸痛", "上腹痛", "下腹痛", "腰背痛", "关节痛", "肌肉痛", "会阴痛", "全身多发痛"],
            "nature": ["撕裂痛", "绞痛", "烧灼痛", "刺痛", "钝痛", "酸痛"],
            "risk": ["Ⅰ级", "Ⅱ级", "Ⅲ级", "Ⅳ级"],
        },
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()
