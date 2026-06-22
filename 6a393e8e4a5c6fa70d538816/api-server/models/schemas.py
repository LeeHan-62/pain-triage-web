from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ConsultationInput(BaseModel):
    location: str = ""
    nature: str = ""
    duration: str = ""
    factor: str = ""
    symptoms: List[str] = Field(default_factory=list)
    description: str = ""
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None


class RiskResult(BaseModel):
    level: str
    label: str
    desc: str
    color: str


class TriageResult(BaseModel):
    location: str
    nature: str
    risk: RiskResult
    department: str
    summary: str
    emotion: Dict[str, Any] = Field(default_factory=dict)
    structured: Dict[str, Any] = Field(default_factory=dict)
    saved_to_openemr: bool = False
    model_sources: Dict[str, str] = Field(default_factory=dict)


class TriageResponse(BaseModel):
    result: TriageResult
    warnings: List[str] = Field(default_factory=list)
