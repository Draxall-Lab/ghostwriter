from datetime import date, datetime
import re 

from .write_policy import (
    WritePolicy,
)

def strip_incoming_contribution_header(content: str) -> str:
    """
    Remove model-supplied contribution/comment headers before applying
    the governed append style.
    """

    lines = content.strip().splitlines()

    while lines and not lines[0].strip():
        lines.pop(0)

    if not lines:
        return ""

    header_pattern = re.compile(
        r"^\*{0,2}\s*(Contribution|Append|Comment)\s+by\s+.+?\s+at\s+.+?\*{0,2}\s*$",
        re.IGNORECASE,
    )

    if header_pattern.match(lines[0].strip()):
        lines = lines[1:]

    while lines and not lines[0].strip():
        lines.pop(0)

    return "\n".join(lines).strip()

def sanitise_note_title(title: str) -> str:
    cleaned = title.strip()

    if not cleaned:
        raise ValueError("Note title is required")

    if any(part in cleaned for part in ["..", "/", "\\"]):
        raise ValueError("Note title must not contain path separators")

    cleaned = re.sub(r'[<>:"|?*]', "", cleaned)

    if not cleaned:
        raise ValueError("Note title is invalid after sanitising")

    return cleaned


def extract_frontmatter(template_text: str) -> str:
    if not template_text.startswith("---"):
        raise ValueError("Template does not contain YAML frontmatter")

    parts = template_text.split("---", 2)

    if len(parts) < 3:
        raise ValueError("Template frontmatter is not properly closed")

    return parts[1].strip()


def update_frontmatter(frontmatter: str, persona_name: str) -> str:
    today = date.today().isoformat()
    lines = frontmatter.splitlines()
    updated_lines = []

    replacements = {
        "created": today,
        "last_updated": today,
        "created_by": "ghostwriter",
        "author": persona_name,
    }

    seen = set()

    for line in lines:
        stripped = line.strip()

        if ":" not in stripped or stripped.startswith("#"):
            updated_lines.append(line)
            continue

        key = stripped.split(":", 1)[0].strip()

        if key in replacements:
            indent = line[: len(line) - len(line.lstrip())]
            updated_lines.append(f"{indent}{key}: {replacements[key]}")
            seen.add(key)
        else:
            updated_lines.append(line)

    for key, value in replacements.items():
        if key not in seen:
            updated_lines.append(f"{key}: {value}")

    return "\n".join(updated_lines).strip()

def current_datetime_string() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def extract_append_contribution_style(meta_ops: dict) -> str:
    """
    Return the Append Contribution Style directive
    from parsed meta-ops sections.
    """

    if not meta_ops:
        return ""

    sections = meta_ops.get("sections") or {}

    section = sections.get("append_contribution_style")

    if not section:
        return ""

    directive = section.get("directive")

    if not directive:
        return ""

    return directive.strip()

def preprocess_contribution(
    content: str,
    meta_ops: dict,
    persona_name: str,
    contribution_type: str = "Contribution",
) -> str:
    
    content = strip_incoming_contribution_header(content)

    style = extract_append_contribution_style(meta_ops)

    if not style or style.strip().lower() == "none":
        return content

    rendered_header = (
        style
        .replace("{persona_name}", persona_name)
        .replace("{current_datetime}", current_datetime_string())
        .replace("{contribution_type}", contribution_type)
    )

    return f"\n\n{rendered_header}\n{content.strip()}\n"

def preprocess_note_update(
    existing_text: str,
    incoming_content: str,
    meta_ops: dict,
    persona_name: str,
    contribution_type: str = "Contribution",
) -> str:

    existing_text = update_last_updated_field(
        existing_text,
        persona_name,
    )

    if contribution_type == "Comment":
        incoming_content = f"*{incoming_content.strip()}*"

    processed_content = preprocess_contribution(
        content=incoming_content,
        meta_ops=meta_ops,
        persona_name=persona_name,
        contribution_type=contribution_type,
    )

    return f"{existing_text.rstrip()}\n\n{processed_content.strip()}\n"

def update_last_updated_field(text: str, persona_name: str | None = None) -> str:
    if not text.startswith("---"):
        return text

    closing = text.find("\n---", 3)

    if closing == -1:
        return text

    frontmatter = text[:closing]
    body = text[closing:]

    updated_value = datetime.now().strftime("%Y-%m-%d %H:%M")

    frontmatter = re.sub(
        r"^last updated\s*:.*$",
        f"last updated: {updated_value}",
        frontmatter,
        flags=re.MULTILINE,
    )

    if persona_name and re.search(r"^last updated by\s*:", frontmatter, re.MULTILINE):
        frontmatter = re.sub(
            r"^last updated by\s*:.*(?:\n\s*-\s*.*)*",
            "",
            frontmatter,
            flags=re.MULTILINE,
        )

        frontmatter += f"\nlast updated by: {persona_name}"

    return frontmatter + body