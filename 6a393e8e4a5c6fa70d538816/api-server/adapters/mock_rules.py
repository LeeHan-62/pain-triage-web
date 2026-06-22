from typing import Dict, Any
from models.schemas import ConsultationInput


LOCATION_MAP = {
    "头": "头痛",
    "胸": "胸痛",
    "腹": "腹痛",
    "腰背": "腰背痛",
    "四肢关节": "关节痛",
    "全身": "全身多发痛",
}

DEPARTMENT_MAP = {
    "头": "神经内科",
    "胸": "心内科/胸外科",
    "腹": "普外科/消化内科",
    "腰背": "骨科/康复科",
    "四肢关节": "骨科",
    "全身": "全科",
}


def contains_any(text: str, words: list[str]) -> bool:
    return any(word in text for word in words)


def local_triage(data: ConsultationInput) -> Dict[str, Any]:
    text = f"{data.location}{data.nature}{data.duration}{data.factor}{' '.join(data.symptoms)}{data.description}"
    location = LOCATION_MAP.get(data.location, data.location or "未明确")
    nature = data.nature or "未明确"

    if (
        (data.location == "胸" and (data.nature == "撕裂痛" or contains_any(text, ["压榨", "大汗", "胸闷"])))
        or (data.location == "腹" and contains_any(text, ["刀割", "剧烈", "呕血"]))
        or (data.location == "腰背" and contains_any(text, ["突发", "剧烈", "撕裂"]))
    ):
        risk = {"level": "Ⅰ级", "label": "极高危", "desc": "立即急诊抢救", "color": "risk-1"}
        department = "急诊科"
    elif (
        (data.location == "头" and contains_any(text, ["持续", "剧烈", "呕吐"]))
        or (data.location == "腹" and contains_any(text, ["压痛", "发热"]))
        or contains_any(text, ["下肢肿痛", "肿胀"])
    ):
        risk = {"level": "Ⅱ级", "label": "高危", "desc": "优先就诊，10分钟内接诊", "color": "risk-2"}
        department = "优先诊室"
    elif contains_any(text, ["急性", "扭伤", "新发", "一过性"]) or data.duration in ["突发几小时", "持续数日"]:
        risk = {"level": "Ⅲ级", "label": "普通急症", "desc": "当日全科优先", "color": "risk-3"}
        department = DEPARTMENT_MAP.get(data.location, "全科")
    else:
        risk = {"level": "Ⅳ级", "label": "慢性慢病", "desc": "常规排队，慢病管理", "color": "risk-4"}
        department = DEPARTMENT_MAP.get(data.location, "全科")

    symptoms = "、".join(data.symptoms) if data.symptoms else "无"
    summary = (
        f"患者主诉{data.location or '某部位'}疼痛，性质倾向为{data.nature or '未明确'}，"
        f"病程为{data.duration or '未明确'}，诱发/缓解因素为{data.factor or '未明确'}，"
        f"伴随症状：{symptoms}。AI 初步判断为{location}，风险等级为{risk['level']}（{risk['label']}）。"
    )

    return {
        "location": location,
        "nature": nature,
        "risk": risk,
        "department": department,
        "summary": summary,
        "structured": data.model_dump(),
    }
