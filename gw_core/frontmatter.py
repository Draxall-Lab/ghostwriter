import re
from typing import Any

import yaml

from datetime import date, datetime

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