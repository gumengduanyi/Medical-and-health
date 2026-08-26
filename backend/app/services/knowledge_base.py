from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeDocument:
    id: str
    title: str
    source_type: str
    content: str
    tags: tuple[str, ...] = ()


def get_knowledge_documents() -> list[KnowledgeDocument]:
    return [
        KnowledgeDocument(
            id="kb_hypertension_01",
            title="高血压管理要点",
            source_type="knowledge",
            content="高血压管理应优先关注连续血压趋势、低盐饮食、规律作息、按医嘱监测和复诊。不要根据单次结果自行停药或调整处方药剂量。",
            tags=("血压", "高血压", "复诊"),
        ),
        KnowledgeDocument(
            id="kb_aspirin_01",
            title="阿司匹林用药提醒",
            source_type="knowledge",
            content="阿司匹林属于常见抗血小板药物，使用前应确认过敏史、既往出血风险和医嘱剂量。若出现黑便、呕血或明显出血，请及时就医。",
            tags=("阿司匹林", "用药", "出血"),
        ),
        KnowledgeDocument(
            id="kb_report_01",
            title="体检报告确认规则",
            source_type="knowledge",
            content="OCR 结果应先由用户确认再作为正式健康资料。未确认内容只能作为识别结果，不能直接作为医疗结论依据。",
            tags=("报告", "OCR", "确认"),
        ),
        KnowledgeDocument(
            id="kb_emergency_01",
            title="紧急症状分流",
            source_type="knowledge",
            content="如果出现胸痛、呼吸困难、意识模糊、持续高热、严重出血或晕厥，应优先提示线下急诊或及时就医，不要仅依赖在线问答。",
            tags=("急症", "胸痛", "呼吸困难"),
        ),
    ]