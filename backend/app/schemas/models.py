from typing import Any

from pydantic import BaseModel, Field


class HealthProfile(BaseModel):
    id: str = "profile_001"
    name: str = "王先生"
    sex: str = "男"
    age: int = 60
    height: int = 172
    weight: int = 68
    allergy: str = "无"
    disease: str = "高血压"
    family_history: str = Field(default="无", alias="familyHistory")

    model_config = {"populate_by_name": True}


class Medicine(BaseModel):
    id: str = ""
    name: str
    dose: str = ""
    stock: int = 0
    expire: str = ""
    risk: str = ""


class MedicalRecord(BaseModel):
    id: str = ""
    title: str
    date: str = ""
    status: str = "已确认"
    content: str = ""


class OcrConfirmRequest(BaseModel):
    source_type: str = Field(default="report", alias="sourceType")
    title: str = ""
    fields: list[dict[str, Any]] = Field(default_factory=list)
    texts: list[str] = Field(default_factory=list)
    stored_file: str = Field(default="", alias="storedFile")
    output_dir: str = Field(default="", alias="outputDir")
    profile_id: str = Field(default="profile_001", alias="profileId")

    model_config = {"populate_by_name": True}


class OcrConfirmResponse(BaseModel):
    source_type: str = Field(alias="sourceType")
    record: MedicalRecord | None = None
    medicine: Medicine | None = None
    message: str

    model_config = {"populate_by_name": True}


class ChatRequest(BaseModel):
    message: str = ""
    context: dict[str, Any] | None = None


class RagSource(BaseModel):
    id: str
    title: str
    source_type: str
    excerpt: str
    score: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    role: str = "assistant"
    content: str
    sources: list[RagSource] = Field(default_factory=list)
    safety_notice: str = "回答仅供健康资料整理与风险提示，不替代医生诊断。"
    requires_clinician: bool = False
