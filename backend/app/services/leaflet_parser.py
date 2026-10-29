import html
import re

TARGET_LEAFLET_SECTIONS = ("作用功效", "用法用量", "禁忌")
LEAFLET_SECTION_BOUNDARIES = (
    "药品名称",
    "成份",
    "成分",
    "性状",
    "适应症",
    "功能主治",
    "主要功效",
    "适用病症",
    "规格",
    "用法用量",
    "不良反应",
    "禁忌",
    "药品禁忌",
    "注意事项",
    "孕妇及哺乳期妇女用药",
    "儿童用药",
    "老年用药",
    "药物相互作用",
    "药物过量",
    "药理毒理",
    "药代动力学",
    "贮藏",
    "贮藏方法",
    "包装",
    "有效期",
    "执行标准",
    "批准文号",
    "生产企业",
    "药性分析",
)
SECTION_ALIASES = {
    "作用功效": "作用功效",
    "作用与功效": "作用功效",
    "功效": "作用功效",
    "功能主治": "作用功效",
    "主要功效": "作用功效",
    "适用病症": "作用功效",
    "适应症": "作用功效",
    "用法用量": "用法用量",
    "禁忌": "禁忌",
    "药品禁忌": "禁忌",
    "禁忌症": "禁忌",
}

def _normalise_text(text: str) -> str:
    text = html.unescape(text).replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    noise_lines = {"播报", "编辑", "讨论", "收藏", "赞", "上传视频"}
    return re.sub(
        r"\n{3,}",
        "\n\n",
        "\n".join(line for line in lines if line and line not in noise_lines),
    ).strip()


def _split_sections(text: str) -> list[tuple[str, str]]:
    section_names = (*LEAFLET_SECTION_BOUNDARIES, *SECTION_ALIASES.keys())
    pattern = re.compile(
        rf"^\s*(?:[一二三四五六七八九十]+[、.．]\s*)?(?P<section>{'|'.join(map(re.escape, section_names))})\s*(?:[:：]\s*(?P<inline>.*))?$"
    )
    sections: list[tuple[str, str]] = []
    current_name: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        if current_name is None:
            return
        content = _normalise_text("\n".join(current_lines))
        if content:
            sections.append((current_name, content))

    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            flush()
            current_name = SECTION_ALIASES.get(match.group("section"), match.group("section"))
            current_lines = [match.group("inline")] if match.group("inline") else []
        elif current_name is not None:
            current_lines.append(line)

    flush()
    if not sections:
        return [("全文", text)]
    return sections


def _filter_target_sections(sections: list[tuple[str, str]]) -> list[tuple[str, str]]:
    selected: list[tuple[str, str]] = []
    for section_name, content in sections:
        canonical_name = SECTION_ALIASES.get(section_name, section_name)
        if canonical_name in TARGET_LEAFLET_SECTIONS:
            selected.append((canonical_name, content))
    return selected
