import os
from typing import Dict, Any
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import ConsultationInput, TriageResponse
from adapters.mock_rules import local_triage
from adapters.fastchat_client import extract_structured_text
from adapters.monai_client import classify_with_monai
from adapters.emotion_client import classify_emotion, mock_emotion
from adapters.openemr_client import save_to_openemr


load_dotenv()

app = FastAPI(title="疼痛智能分诊模型接入层", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_monai_result(monai_result: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    location = monai_result.get("location") or monai_result.get("part") or fallback["location"]
    nature = monai_result.get("nature") or fallback["nature"]
    risk_value = monai_result.get("risk") or monai_result.get("risk_level") or fallback["risk"]["level"]

    risk_map = {
        "Ⅰ级": {"level": "Ⅰ级", "label": "极高危", "desc": "立即急诊抢救", "color": "risk-1"},
        "Ⅱ级": {"level": "Ⅱ级", "label": "高危", "desc": "优先就诊，10分钟内接诊", "color": "risk-2"},
        "Ⅲ级": {"level": "Ⅲ级", "label": "普通急症", "desc": "当日全科优先", "color": "risk-3"},
        "Ⅳ级": {"level": "Ⅳ级", "label": "慢性慢病", "desc": "常规排队，慢病管理", "color": "risk-4"},
    }
    risk = risk_map.get(risk_value, fallback["risk"])

    department = fallback["department"]
    if risk["level"] == "Ⅰ级":
        department = "急诊科"
    elif "头" in location:
        department = "神经内科"
    elif "胸" in location:
        department = "心内科/胸外科"
    elif "腹" in location:
        department = "普外科/消化内科"
    elif "关节" in location or "腰背" in location:
        department = "骨科"

    fallback.update({
        "location": location,
        "nature": nature,
        "risk": risk,
        "department": department,
    })
    fallback["summary"] = (
        f"模型判断为{location}，疼痛性质为{nature}，风险等级为{risk['level']}（{risk['label']}），"
        f"建议分流至{department}。"
    )
    return fallback


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "mode": os.getenv("APP_MODE", "mock"),
        "services": {
            "fastchat": bool(os.getenv("FASTCHAT_BASE_URL")),
            "monai": bool(os.getenv("MONAI_API_URL")),
            "kobert_emotion": bool(os.getenv("KOBERT_EMOTION_API_URL")),
            "openemr": bool(os.getenv("OPENEMR_BASE_URL") and os.getenv("OPENEMR_ACCESS_TOKEN")),
        },
    }


@app.post("/api/triage", response_model=TriageResponse)
async def triage_api(data: ConsultationInput):
    mode = os.getenv("APP_MODE", "mock").lower()
    warnings = []
    model_sources = {}

    fallback = local_triage(data)
    structured = fallback["structured"]

    if mode in ["hybrid", "real"]:
        try:
            structured = await extract_structured_text(data)
            model_sources["fastchat"] = "real"
        except Exception as exc:
            warnings.append(f"FastChat 未完成调用，已使用本地结构化信息：{exc}")
            model_sources["fastchat"] = "mock"

        try:
            monai_result = await classify_with_monai(data, structured)
            fallback = normalize_monai_result(monai_result, fallback)
            model_sources["monai"] = "real"
        except Exception as exc:
            warnings.append(f"MONAI 未完成调用，已使用本地分级规则：{exc}")
            model_sources["monai"] = "mock"

        try:
            emotion = await classify_emotion(data)
            model_sources["kobert_emotion"] = "real"
        except Exception as exc:
            warnings.append(f"KoBERT-Emotion 未完成调用，已使用本地情绪强度估计：{exc}")
            emotion = mock_emotion(data)
            model_sources["kobert_emotion"] = "mock"
    else:
        emotion = mock_emotion(data)
        model_sources = {
            "fastchat": "mock",
            "monai": "mock",
            "kobert_emotion": "mock",
        }

    result = {
        **fallback,
        "emotion": emotion,
        "structured": structured,
        "saved_to_openemr": False,
        "model_sources": model_sources,
    }

    if mode in ["hybrid", "real"]:
        try:
            result["saved_to_openemr"] = await save_to_openemr(data, result)
            model_sources["openemr"] = "real"
        except Exception as exc:
            warnings.append(f"OpenEMR 未写入，已保留前端本地档案：{exc}")
            model_sources["openemr"] = "mock"
    else:
        model_sources["openemr"] = "mock"

    return {"result": result, "warnings": warnings}
