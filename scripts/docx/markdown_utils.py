from __future__ import annotations

import re


SCREENSHOT_PLACEHOLDER_RE = re.compile(r"^\[此处插入截图：(.+?)\]$")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
AUTOLINK_RE = re.compile(r"<(https?://[^>]+)>")


def cleanup_inline_markdown(text: str) -> str:
    cleaned = text.replace("`", "")
    cleaned = LINK_RE.sub(r"\1", cleaned)
    cleaned = AUTOLINK_RE.sub(r"\1", cleaned)

    # Remove emphasis markers but keep their content.
    for pattern in (
        (r"\*\*(.+?)\*\*", r"\1"),
        (r"__(.+?)__", r"\1"),
        (r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"\1"),
        (r"(?<!_)_(?!\s)(.+?)(?<!\s)_(?!_)", r"\1"),
    ):
        cleaned = re.sub(pattern[0], pattern[1], cleaned)

    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def markdown_to_visible_text(text: str) -> str:
    lines: list[str] = []
    in_code = False

    for raw_line in text.splitlines():
        stripped = raw_line.strip()

        if stripped.startswith("```"):
            in_code = not in_code
            continue

        if in_code or not stripped:
            continue

        if stripped == "---":
            continue

        if SCREENSHOT_PLACEHOLDER_RE.match(stripped):
            continue

        if stripped.startswith("|"):
            cells = [cleanup_inline_markdown(cell) for cell in stripped.strip("|").split("|")]
            if all(re.fullmatch(r"[:\- ]+", cell or "") for cell in cells):
                continue
            lines.append(" ".join(cell for cell in cells if cell))
            continue

        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()

        lines.append(cleanup_inline_markdown(stripped))

    return "\n".join(line for line in lines if line)


def compute_text_metrics(text: str) -> dict[str, int]:
    visible = markdown_to_visible_text(text)
    char_with_spaces = len(visible)
    char_no_spaces = len(re.sub(r"\s+", "", visible))
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", visible))
    non_chinese_words = len(re.findall(r"[A-Za-z0-9]+(?:[._/\-'][A-Za-z0-9]+)*", visible))
    english_words = len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", visible))
    approx_word_count = chinese_chars + non_chinese_words

    return {
        "char_with_spaces": char_with_spaces,
        "char_no_spaces": char_no_spaces,
        "chinese_chars": chinese_chars,
        "non_chinese_words": non_chinese_words,
        "english_words": english_words,
        "approx_word_count": approx_word_count,
    }
