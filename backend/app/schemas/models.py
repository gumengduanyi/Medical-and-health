from typing import Any

from pydantic import BaseModel, Field


class AuthLoginRequest(BaseModel):
    code: str = ""
    nickname: str = "微信用户"
    avatar_url: str = Field(default="", alias="avatarUrl")

    model_config = {"populate_by_name": True}


class UserProfile(BaseModel):
    id: str
    openid: str = ""
    nickname: str = "微信用户"
    avatar_url: str = Field(default="", alias="avatarUrl")

    model_config = {"populate_by_name": True}


class AuthLoginResponse(BaseModel):
    token: str
    access_token: str = Field(alias="accessToken")
    user: UserProfile
    expires_in: int = Field(alias="expiresIn")

    model_config = {"populate_by_name": True}


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
    specification: str = ""
    manufacturer: str = ""
    approval_number: str = ""
    stock: int = 0
    expire: str = ""
    risk: str = ""
    image_path: str = Field(default="", alias="imagePath")
    ocr_output_dir: str = Field(default="", alias="ocrOutputDir")

    model_config = {"populate_by_name": True}


class LeafletImportRequest(BaseModel):
    generic_name: str
    brand_name: str = ""
    dosage_form: str = ""
    specification: str = ""
    manufacturer: str = ""
    approval_number: str = ""
    published_at: str = ""
    candidate_id: str = ""
    content_hash: str = ""
    confirmed: bool = False


class LeafletDiscoverRequest(BaseModel):
    generic_name: str
    manufacturer: str = ""
    approval_number: str = ""
    specification: str = ""


class LeafletCandidate(BaseModel):
    source_type: str
    source_url: str
    title: str = ""
    confidence: float
    candidate_id: str = ""
    content_hash: str = ""
    authority: str = "encyclopedia"
    missing_identity_fields: list[str] = Field(default_factory=list)
    conflicting_fields: list[str] = Field(default_factory=list)
    sections_found: list[str] = Field(default_factory=list)
    sections: dict[str, str] = Field(default_factory=dict)
    missing_sections: list[str] = Field(default_factory=list)
    matched_fields: list[str] = Field(default_factory=list, alias="matchedFields")
    mismatched_fields: list[str] = Field(default_factory=list, alias="mismatchedFields")
    http_status: int = Field(default=0, alias="httpStatus")
    attempts: int = 1
    elapsed_ms: int = Field(default=0, alias="elapsedMs")
    status: str = "candidate"
    reason: str = ""

    model_config = {"populate_by_name": True}


class LeafletDiscoverResponse(BaseModel):
    generic_name: str
    candidates: list[LeafletCandidate] = Field(default_factory=list)


class LeafletReviewRequest(BaseModel):
    note: str = ""


class LeafletSection(BaseModel):
    id: str
    section_name: str
    section_order: int
    content: str


class LeafletImportResponse(BaseModel):
    id: str
    generic_name: str
    brand_name: str
    dosage_form: str
    specification: str
    manufacturer: str
    approval_number: str
    source_url: str
    source_type: str
    raw_file_path: str
    content_type: str
    content_hash: str
    status: str
    confirmed_by: str = ""
    confirmed_at: str | None = None
    index_status: str = "pending"
    reviewed_by: str = Field(default="", alias="reviewedBy")
    reviewed_at: str | None = Field(default=None, alias="reviewedAt")
    review_note: str = Field(default="", alias="reviewNote")
    sections: list[LeafletSection] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class MedicalRecordItem(BaseModel):
    id: str = ""
    position: int = 0
    label: str
    value: str = ""
    unit: str = ""
    reference: str = ""
    status: str = "normal"


class MedicalRecord(BaseModel):
    id: str = ""
    title: str
    date: str = ""
    status: str = "已确认"
    content: str = ""
    items: list[MedicalRecordItem] = Field(default_factory=list)


class OcrConfirmRequest(BaseModel):
    confirmed: bool = False
    record_date: str = Field(default="", alias="recordDate")
    source_type: str = Field(default="report", alias="sourceType")
    title: str = ""
    fields: list[dict[str, Any]] = Field(default_factory=list)
    texts: list[str] = Field(default_factory=list)
    stored_file: str = Field(default="", alias="storedFile")
    output_dir: str = Field(default="", alias="outputDir")
    profile_id: str = Field(default="profile_001", alias="profileId")
    leaflet_candidate: LeafletCandidate | None = Field(default=None, alias="leafletCandidate")

    model_config = {"populate_by_name": True}


class OcrConfirmResponse(BaseModel):
    source_type: str = Field(alias="sourceType")
    record: MedicalRecord | None = None
    medicine: Medicine | None = None
    leaflet_candidate: LeafletCandidate | None = Field(default=None, alias="leafletCandidate")
    leaflet: LeafletImportResponse | None = None
    message: str

    model_config = {"populate_by_name": True}


class ReportAttachment(BaseModel):
    name: str = ""
    url: str = ""
    size: int = 0


class ReportOcrPayload(BaseModel):
    fields: list[dict[str, Any]] = Field(default_factory=list)
    texts: list[str] = Field(default_factory=list)
    stored_file: str = Field(default="", alias="storedFile")
    output_dir: str = Field(default="", alias="outputDir")

    model_config = {"populate_by_name": True}


class ReportCreateRequest(BaseModel):
    confirmed: bool = False
    name: str
    category: str = "体检报告"
    entry_time: str = Field(default="", alias="entryTime")
    report_time: str = Field(default="", alias="reportTime")
    remark: str = ""
    images: list[ReportAttachment] = Field(default_factory=list)
    files: list[ReportAttachment] = Field(default_factory=list)
    ocr: ReportOcrPayload = Field(default_factory=ReportOcrPayload)

    model_config = {"populate_by_name": True}


class ReportCreateResponse(BaseModel):
    id: str
    record_id: str = Field(alias="recordId")
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
