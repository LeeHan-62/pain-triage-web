import os
from typing import Dict, Any, Optional
import httpx
from models.schemas import ConsultationInput


async def save_to_openemr(data: ConsultationInput, result: Dict[str, Any]) -> bool:
    base_url = os.getenv("OPENEMR_BASE_URL", "").rstrip("/")
    token = os.getenv("OPENEMR_ACCESS_TOKEN", "")
    patient_id = data.patient_id or os.getenv("OPENEMR_PATIENT_ID", "")

    if not base_url or not token or not patient_id:
        raise RuntimeError("未配置 OPENEMR_BASE_URL、OPENEMR_ACCESS_TOKEN 或患者 ID")

    encounter_payload = {
        "pc_catid": "10",
        "reason": "疼痛智能问诊分诊",
        "facility": "智能分诊系统",
        "billing_facility": "智能分诊系统",
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=30) as client:
        encounter_resp = await client.post(
            f"{base_url}/patient/{patient_id}/encounter",
            headers=headers,
            json=encounter_payload,
        )
        encounter_resp.raise_for_status()

        clinical_note = {
            "note": result.get("summary", ""),
            "risk_level": result.get("risk", {}).get("level"),
            "risk_label": result.get("risk", {}).get("label"),
            "department": result.get("department"),
            "emotion": result.get("emotion", {}),
            "structured": result.get("structured", {}),
        }

        note_resp = await client.post(
            f"{base_url}/patient/{patient_id}/document",
            headers=headers,
            json={
                "name": "疼痛智能分诊记录",
                "type": "clinical_note",
                "content": clinical_note,
            },
        )
        note_resp.raise_for_status()

    return True
