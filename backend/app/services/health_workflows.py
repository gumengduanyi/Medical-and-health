from datetime import date
from decimal import Decimal, InvalidOperation
import re


def verify_fields(fields):
    issues = []
    seen = set()
    for index, field in enumerate(fields):
        label = str(field.get("label", "")).strip()
        value = str(field.get("value", "")).strip()
        if not label or not value:
            issues.append({"index": index, "code": "missing", "message": "字段名称或值为空"})
        key = (label, value, field.get("unit", ""))
        if key in seen:
            issues.append({"index": index, "code": "duplicate", "message": "发现重复字段，请核对"})
        seen.add(key)
        if "日期" in label and value:
            try:
                date.fromisoformat(value)
            except ValueError:
                issues.append({"index": index, "code": "date", "message": "请确认日期并使用 YYYY-MM-DD"})
        if field.get("status") == "pending" or field.get("confidence", 1) < 0.8:
            issues.append({"index": index, "code": "uncertain", "message": "识别结果需要人工核对"})
    return {"issues": issues, "requires_confirmation": True, "field_count": len(fields)}


def inspect_cabinet(medicines, today, low_stock, expiry_days):
    findings = []
    identities = {}
    for medicine in medicines:
        mid = medicine.id
        def add(code, message):
            findings.append({"medicine_id": mid, "name": medicine.name, "code": code, "message": message})
        if medicine.stock <= low_stock:
            add("low_stock", "库存达到补货阈值，请核对实际库存")
        try:
            remaining = (date.fromisoformat(medicine.expire) - today).days
            if remaining < 0:
                add("expired", "已超过记录的有效期，请核对")
            elif remaining <= expiry_days:
                add("expiring", f"记录的有效期剩余 {remaining} 天")
        except ValueError:
            add("unknown_expiry", "有效期缺失或格式不明确")
        if not medicine.approval_number or not medicine.manufacturer or not medicine.specification:
            add("missing_identity", "厂家、规格或批准文号不完整")
        key = (medicine.approval_number.strip(), medicine.specification.strip(), medicine.manufacturer.strip())
        if all(key):
            if key in identities:
                add("possible_duplicate", f"可能与记录 {identities[key]} 重复，请核对批次")
            identities[key] = mid
    return {"findings": findings, "as_of": today.isoformat(), "notice": "仅核查库存和资料，不构成用药方案。"}


def analyze_trends(records):
    groups = {}
    excluded = []
    for record in records:
        if record.status != "已确认":
            excluded.append({"record_id": record.id, "reason": "资料尚未确认"})
            continue
        try:
            when = date.fromisoformat(record.date)
        except ValueError:
            excluded.append({"record_id": record.id, "reason": "检查日期无效"})
            continue
        for item in record.items:
            try:
                if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", item.value.strip()):
                    raise ValueError()
                value = Decimal(item.value)
                if not value.is_finite() or not item.unit.strip():
                    raise ValueError()
            except (ValueError, InvalidOperation):
                excluded.append({"record_id": record.id, "label": item.label, "reason": "非明确数值或缺少单位"})
                continue
            key = (item.label.strip(), item.unit.strip())
            groups.setdefault(key, []).append({"date": when.isoformat(), "value": str(value), "reference": item.reference, "record_id": record.id})
    trends = []
    for (label, unit), points in sorted(groups.items()):
        points.sort(key=lambda item: (item["date"], item["record_id"]))
        comparable = len(points) > 1 and len({p["date"] for p in points}) == len(points)
        delta = str(Decimal(points[-1]["value"]) - Decimal(points[0]["value"])) if comparable else None
        trends.append({"label": label, "unit": unit, "points": points, "delta": delta, "reference_changed": len({p["reference"] for p in points}) > 1})
    return {"trends": trends, "excluded": excluded, "notice": "不同单位分别展示；数值变化不代表诊断，参考范围变化需核对。"}
