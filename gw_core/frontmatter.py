import re
from typing import Any

import yaml

from datetime import date, datetime

from pathlib import Path

from .write_policy import (
    WritePolicy,
    clean_path_input,
)

FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n?",
    re.DOTALL
)


def split_frontmatter(content: str) -> dict[str, Any]:
    """
    Split a Markdown note into:
    - raw frontmatter text
    - parsed frontmatter dict
    - body content

    Always fails safely.
    """

    result = {
        "has_frontmatter": False,
        "frontmatter_raw": "",
        "frontmatter": {},
        "frontmatter_status": {
            "present": False,
            "parsed": False,
            "error": None
        },
        "body": content
    }

    if not content or not content.startswith("---"):
        return result

    match = FRONTMATTER_PATTERN.match(content)

    if not match:
        return result

    raw_frontmatter = match.group(1)
    body = content[match.end():]

    result["has_frontmatter"] = True
    result["frontmatter_raw"] = raw_frontmatter
    result["body"] = body

    result["frontmatter_status"]["present"] = True

    try:
        parsed = yaml.safe_load(raw_frontmatter)

        if parsed is None:
            parsed = {}

        if not isinstance(parsed, dict):
            raise ValueError("Frontmatter must parse to a dictionary")

        parsed = normalise_frontmatter(parsed)
        parsed = make_json_safe(parsed)

        result["frontmatter"] = parsed
        result["frontmatter_status"]["parsed"] = True

    except Exception as exc:
        result["frontmatter_status"]["error"] = str(exc)

    return result


def normalise_frontmatter(data: dict[str, Any]) -> dict[str, Any]:
    """
    Normalise common frontmatter fields into predictable shapes.
    """

    normalised = dict(data)

    if "author" in normalised:
        normalised["author"] = normalise_author(
            normalised.get("author")
        )

    if "tags" in normalised:
        normalised["tags"] = normalise_tags(
            normalised.get("tags")
        )

    return normalised


def normalise_author(value) -> list[str]:
    """
    Always return authors as a list of strings.
    """

    if value is None:
        return []

    if isinstance(value, str):
        return [value.strip()]

    if isinstance(value, list):
        authors = []

        for item in value:
            if item is None:
                continue

            text = str(item).strip()

            if text:
                authors.append(text)

        return authors

    return [str(value).strip()]


def normalise_tags(value) -> list[str]:
    """
    Always return tags as a list of strings.
    """

    if value is None:
        return []

    if isinstance(value, str):
        return [
            tag.strip()
            for tag in value.split(",")
            if tag.strip()
        ]

    if isinstance(value, list):
        tags = []

        for item in value:
            if item is None:
                continue

            text = str(item).strip()

            if text:
                tags.append(text)

        return tags

    return [str(value).strip()]

def make_json_safe(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [make_json_safe(item) for item in value]

    if isinstance(value, tuple):
        return [make_json_safe(item) for item in value]

    return value

def insert_frontmatter(
    vault_root: Path,
    policy: WritePolicy,
    note_path: str,
    frontmatter: dict,
) -> Path:
    from .governance import preprocess_note_metadata_update
    from .meta import read_meta_ops
    from .governance import can_perform_note_action
    from .write_policy import resolve_existing_vault_note_path

    if not note_path or not note_path.strip():
        raise ValueError("note_path is required")

    if not frontmatter:
        raise ValueError("frontmatter is required")

    note_path = clean_path_input(note_path)

    target = resolve_existing_vault_note_path(vault_root, note_path)

    if not can_perform_note_action(
        vault_root=vault_root,
        persona=policy.persona_name,
        note_path=note_path,
        action="edit",
    ):
        raise PermissionError("Blocked, ask user for permission")

    if not target.exists():
        raise FileNotFoundError(f"Note not found: {note_path}")

    meta_ops = read_meta_ops(vault_root)

    existing_text = target.read_text(encoding="utf-8")

    updated_text = preprocess_note_metadata_update(
        existing_text=existing_text,
        meta_ops=meta_ops,
        persona_name=policy.persona_name,
        frontmatter=frontmatter,
    )

    target.write_text(updated_text, encoding="utf-8")

    return target