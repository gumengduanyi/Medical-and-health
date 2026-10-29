import re


def compare_identity(expected: dict[str, str], text: str) -> dict[str, list[str]]:
    result = {"matched": [], "missing": [], "conflicting": []}
    labels = {
        "通用名": r"(?:通用名称|药品名称)\s*[:：]\s*([^\n]+)",
        "厂家": r"(?:生产企业|生产厂家|上市许可持有人)\s*[:：]\s*([^\n]+)",
        "规格": r"规格\s*[:：]\s*([^\n]+)",
        "批准文号": r"批准文号\s*[:：]\s*([^\n]+)",
    }
    normalize = lambda value: re.sub(r"\s+", "", value).casefold()
    for label, value in expected.items():
        if not value.strip():
            continue
        observed = re.search(labels[label], text)
        if observed:
            state = "matched" if normalize(value) == normalize(observed.group(1)) else "conflicting"
        else:
            state = "matched" if normalize(value) in normalize(text) else "missing"
        result[state].append(label)
    return result
