from datetime import date, datetime
import re 

from .write_policy import (
    WritePolicy,
)

import logging

logger = logging.getLogger(__name__)


DEFAULT_FRONTMATTER_FIELD_MAP = {
    "author": "author",
    "created": "created",
    "created_by": "created by",
    "last_updated": "last updated",
    "last_updated_by": "last updated by",
    "contributor": "contributor",
    "commenter": "commenter",
    "related": "related",
}

PROTECTED_FRONTMATTER_ROLES = {
    "author",
    "created",
    "created_by",
    "last_updated",
    "last_updated_by",
    "contributor",
    "commenter",
}

def preprocess_note_metadata_update(
    existing_text: str,
    meta_ops: dict,
    persona_name: str,
    frontmatter: dict | None = None,
) -> str:
    if frontmatter:
        existing_text = apply_ai_frontmatter_updates_to_existing_note(
            existing_text=existing_text,
            ai_frontmatter=frontmatter,
            meta_ops=meta_ops,
        )

    return apply_mutation_frontmatter_updates(
        existing_text=existing_text,
        meta_ops=meta_ops,
        persona_name=persona_name,
    )

def normalize_related_links(value, limit: int = 5) -> list[str]:
    """
    Normalize related metadata entries into Obsidian wikilinks.

    Accepts a list or scalar value. Empty values are discarded.
    """

    values = value if isinstance(value, list) else [value]
    cleaned = []

    for item in values:
        text = str(item).strip()

        if not text:
            continue

        if text.startswith("[[") and text.endswith("]]"):
            cleaned.append(text)
        else:
            cleaned.append(f"[[{text}]]")

        if len(cleaned) >= limit:
            break

    return cleaned

def merge_list_values(existing, incoming, limit: int | None = None) -> list:
    existing_values = existing if isinstance(existing, list) else [existing]
    incoming_values = incoming if isinstance(incoming, list) else [incoming]

    merged = []

    for item in existing_values + incoming_values:
        if item in (None, "", [], {}):
            continue

        if item not in merged:
            merged.append(item)

        if limit is not None and len(merged) >= limit:
            break

    return merged

def merge_allowed_ai_frontmatter(
    template_frontmatter: dict,
    ai_frontmatter: dict,
    meta_ops: dict,
) -> dict:
    """
    Merge AI-supplied frontmatter into template frontmatter.

    Rules:
    - only fields already present in the template may be updated
    - protected governance fields are never updated from AI input
    - unknown AI fields are discarded
    """

    field_map = get_frontmatter_field_map(meta_ops)

    protected_field_names = {
        field_map[role]
        for role in PROTECTED_FRONTMATTER_ROLES
        if role in field_map
    }

    merged = template_frontmatter.copy()

    for field_name, value in ai_frontmatter.items():
        if field_name not in template_frontmatter:
            continue

        if field_name in protected_field_names:
            continue

        if value in (None, "", [], {}):
            continue

        if field_name == field_map.get("related"):
            value = normalize_related_links(value)

            if not value:
                continue

        existing_value = merged.get(field_name)

        if isinstance(existing_value, list) or isinstance(value, list):
            limit = 5 if field_name == field_map.get("related") else None

            merged[field_name] = merge_list_values(
                existing=existing_value,
                incoming=value,
                limit=limit,
            )
        else:
            merged[field_name] = value
            
    return merged

def pseudo_metadata_enabled(meta_ops: dict) -> bool:
    sections = meta_ops.get("sections") or {}
    section = sections.get("pseudo_metadata_handling") or {}
    directive = section.get("directive", "")

    return (
        isinstance(directive, str)
        and "enabled" in directive.lower()
    )


def parse_pseudo_meta_block(block_text: str) -> dict:
    parsed = {}

    for line in block_text.splitlines():
        line = line.strip()

        if not line or ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue

        if "|" in value:
            parsed[key] = [part.strip() for part in value.split("|") if part.strip()]
        else:
            parsed[key] = value

    return parsed

def extract_leading_pseudo_frontmatter_chain(
    content: str,
    meta_ops: dict,
    max_blocks: int = 2,
) -> tuple[dict, str]:
    combined = {}

    for _ in range(max_blocks):
        extracted, content = extract_pseudo_frontmatter_from_content(
            content=content,
            meta_ops=meta_ops,
        )

        if not extracted:
            break

        combined = {
            **combined,
            **extracted,
        }

    return combined, content

def extract_pseudo_frontmatter_from_content(
    content: str,
    meta_ops: dict,
) -> tuple[dict, str]:
    """
    Extract explicitly bounded pseudo-metadata from the start of incoming AI content.

    Supported only when enabled in meta-ops:
    - leading --- ... --- block
    - leading <meta> ... </meta> block

    Returns:
    - extracted metadata suggestions
    - cleaned content
    """

    if not pseudo_metadata_enabled(meta_ops):
        return {}, content

    leading_len = len(content) - len(content.lstrip())
    leading = content[:leading_len]
    stripped = content.lstrip()

    # YAML-style pseudo-frontmatter
    if stripped.startswith("---"):
        lines = stripped.splitlines()

        if lines and lines[0].strip() == "---":
            closing_index = None

            for index, line in enumerate(lines[1:], start=1):
                if line.strip() == "---":
                    closing_index = index
                    break

            if closing_index is not None:
                block_text = "\n".join(lines[1:closing_index])
                parsed = parse_pseudo_meta_block(block_text)

                if parsed:
                    remaining = "\n".join(lines[closing_index + 1:]).lstrip()
                    return parsed, f"{leading}{remaining}"

    # XML-ish pseudo-meta
    if stripped.lower().startswith("<meta>"):
        close_match = re.search(
            r"</meta>",
            stripped,
            flags=re.IGNORECASE,
        )

        if close_match:
            block_text = stripped[len("<meta>"):close_match.start()]
            parsed = parse_pseudo_meta_block(block_text)

            if parsed:
                remaining = stripped[close_match.end():].lstrip()
                return parsed, f"{leading}{remaining}"

    return {}, content

def clean_mapping_token(value: str) -> str:
    return value.strip().strip("*`_").strip()

def get_frontmatter_field_map(meta_ops: dict) -> dict[str, str]:
    field_map = DEFAULT_FRONTMATTER_FIELD_MAP.copy()

    sections = meta_ops.get("sections") or {}
    mapping_section = sections.get("frontmatter_field_mapping") or {}

    directive = mapping_section.get("directive", "")

    if not isinstance(directive, str):
        return field_map

    for line in directive.splitlines():
        line = line.strip()

        if not line or line.startswith("#") or ":" not in line:
            continue

        internal_name, mapped_name = line.split(":", 1)

        internal_name = internal_name.strip()
        mapped_name = mapped_name.strip()

        internal_name = clean_mapping_token(internal_name)
        mapped_name = clean_mapping_token(mapped_name)

        if internal_name in field_map and mapped_name:
            field_map[internal_name] = mapped_name

    return field_map

def apply_mutation_frontmatter_updates(
    existing_text: str,
    meta_ops: dict,
    persona_name: str,
) -> str:
    """
    Update canonical maintenance fields during append/comment operations.

    Uses field mappings from meta-ops.
    Preserves all unknown frontmatter fields unchanged.
    """

    if not existing_text.startswith("---"):
        return existing_text

    closing = existing_text.find("\n---", 3)

    if closing == -1:
        return existing_text

    frontmatter = existing_text[:closing]
    body = existing_text[closing:]

    field_map = get_frontmatter_field_map(meta_ops)

    last_updated_field = field_map["last_updated"]
    last_updated_by_field = field_map["last_updated_by"]

    updated_value = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = frontmatter.splitlines()
    new_lines = []

    skip_multiline_field = None

    for line in lines:
        stripped = line.strip()

        # Skip list continuation lines for protected fields
        if skip_multiline_field:
            if stripped.startswith("- "):
                continue

            skip_multiline_field = None

        # Update last updated
        if re.match(
            rf"^{re.escape(last_updated_field)}\s*:",
            stripped,
            re.IGNORECASE,
        ):
            new_lines.append(f"{last_updated_field}: {updated_value}")
            continue

        # Update last updated by
        if re.match(
            rf"^{re.escape(last_updated_by_field)}\s*:",
            stripped,
            re.IGNORECASE,
        ):
            new_lines.append(
                f"{last_updated_by_field}: {persona_name}"
            )

            skip_multiline_field = last_updated_by_field
            continue

        new_lines.append(line)

    return "\n".join(new_lines) + body

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

def apply_ai_frontmatter_updates_to_existing_note(
    existing_text: str,
    ai_frontmatter: dict,
    meta_ops: dict,
) -> str:
    """
    Apply governed AI-supplied frontmatter updates to an existing note.

    Rules are inherited from merge_allowed_ai_frontmatter():
    - only existing frontmatter fields may be updated
    - protected governance fields are ignored
    - unknown fields are discarded
    - related is normalised into Obsidian wikilinks
    """

    if not existing_text.startswith("---"):
        return existing_text

    closing = existing_text.find("\n---", 3)

    if closing == -1:
        return existing_text

    frontmatter_text = existing_text[3:closing].strip()
    body = existing_text[closing:]

    template_frontmatter = parse_simple_frontmatter(frontmatter_text)

    merged_frontmatter = merge_allowed_ai_frontmatter(
        template_frontmatter=template_frontmatter,
        ai_frontmatter=ai_frontmatter,
        meta_ops=meta_ops,
    )

    rendered_frontmatter = render_simple_frontmatter(merged_frontmatter)

    return f"---\n{rendered_frontmatter}\n{body}"

def parse_simple_frontmatter(frontmatter_text: str) -> dict:
    parsed = {}
    current_key = None

    for line in frontmatter_text.splitlines():
        if not line.strip():
            continue

        if line.lstrip().startswith("- ") and current_key:
            if not isinstance(parsed.get(current_key), list):
                parsed[current_key] = []

            parsed[current_key].append(line.strip()[2:].strip())
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value == "":
            parsed[key] = ""
            current_key = key
        else:
            parsed[key] = value
            current_key = key

    return parsed

def render_simple_frontmatter(frontmatter: dict) -> str:
    lines = []

    for key, value in frontmatter.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")

    return "\n".join(lines)

def preprocess_note_update(
    existing_text: str,
    incoming_content: str,
    meta_ops: dict,
    persona_name: str,
    contribution_type: str = "Contribution",
    frontmatter: dict | None = None,
) -> str:
    
    pseudo_frontmatter, incoming_content = extract_pseudo_frontmatter_from_content(
        content=incoming_content,
        meta_ops=meta_ops,
    )

    if pseudo_frontmatter:
        frontmatter = {
            **pseudo_frontmatter,
            **(frontmatter or {}),
        }

    if frontmatter:
        existing_text = apply_ai_frontmatter_updates_to_existing_note(
            existing_text=existing_text,
            ai_frontmatter=frontmatter,
            meta_ops=meta_ops,
        )
     
    existing_text = apply_mutation_frontmatter_updates(
        existing_text=existing_text,
        meta_ops=meta_ops,
        persona_name=persona_name,
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