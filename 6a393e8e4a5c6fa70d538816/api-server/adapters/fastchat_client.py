import os
import json
from typing import Dict, Any
import httpx
from models.schemas import ConsultationInput


async def extract_structured_text(data: ConsultationInput) -> Dict[str, Any]:
    base_url = os.getenv("FASTCHAT_BASE_URL", "").rstrip("/")
    model = os.getenv("FASTCHAT_MODEL", "clinical-chat")
    api_key = os.getenv("FASTCHAT_API_KEY", "EMPTY")

    if not base_url:
        raise RuntimeError("未配置 FASTCHAT_BASE_URL")

    prompt = f"""
你是临床疼痛问诊结构化助手。请根据患者输入提取 JSON，不要输出多余文字。
字段包括：location、nature、duration、factor、symptoms、chief_complaint、red_flags。

已选择信息：
疼痛位置：{data.location}
疼痛性质：{data.nature}
疼痛时长：{data.duration}
诱发/缓解因素：{data.factor}
伴随症状：{", ".join(data.symptoms)}
患者描述：{data.description}
"""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你只输出合法 JSON。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "location": data.location,
            "nature": data.nature,
            "duration": data.duration,
            "factor": data.factor,
            "symptoms": data.symptoms,
            "chief_complaint": data.description,
            "red_flags": [],
            "raw_fastchat_output": content,
        }
