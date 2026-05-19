from datetime import date
from pathlib import Path
from typing import Any
import yaml

from .frontmatter import split_frontmatter

from .meta import (
    read_meta_ops,
    get_meta_section_directive,
)

from .governance import (
    get_frontmatter_field_map,
    merge_allowed_ai_frontmatter
)

import logging

logger = logging.getLogger(__name__)


def render_frontmatter(frontmatter: dict[str, Any]) -> str:
    yaml_text = yaml.safe_dump(
        frontmatter,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ).strip()

    return f"---\n{yaml_text}\n---\n"

def strip_frontmatter_block(content: str) -> str:
    """
    Remove any AI-supplied frontmatter from generated note content.

    New-note frontmatter is owned by the template/governance layer.
    """

    parsed = split_frontmatter(content)

    if parsed.get("has_frontmatter"):
        return parsed.get("body", "").lstrip()

    return content.lstrip()

def load_template_frontmatter_for_new_note(
    vault_root: Path,
    persona_name: str,
    ai_frontmatter: dict | None = None,
) -> str | None:
    """
    Load the template path from meta-ops, copy its frontmatter block,
    optionally merge allowed AI-supplied frontmatter fields,
    and patch controlled governance fields for a newly-created note.

    Returns the complete frontmatter block including --- delimiters,
    or None when template use is disabled.
    """

    meta_ops = read_meta_ops(vault_root)

    template_rel_path = get_meta_section_directive(
        meta_ops,
        "template_path",
    )

    if template_rel_path is None:
        return None

    template_rel_path = template_rel_path.strip()

    if not template_rel_path:
        return None

    if template_rel_path.lower() == "none":
        return None

    vault_root = vault_root.resolve()
    template_path = (vault_root / template_rel_path).resolve()

    if not template_path.is_relative_to(vault_root):
        raise ValueError("Template path resolves outside vault")

    if not template_path.exists() or not template_path.is_file():
        raise FileNotFoundError(f"Template not found: {template_rel_path}")

    template_content = template_path.read_text(encoding="utf-8")
    parsed = split_frontmatter(template_content)

    if not parsed.get("has_frontmatter"):
        raise ValueError(f"Template has no frontmatter: {template_rel_path}")

    frontmatter = parsed.get("frontmatter") or {}

    if ai_frontmatter:

        frontmatter = merge_allowed_ai_frontmatter(
            template_frontmatter=frontmatter,
            ai_frontmatter=ai_frontmatter,
            meta_ops=meta_ops,
        )

    today = date.today().isoformat()

    field_map = get_frontmatter_field_map(meta_ops)

    frontmatter[field_map["created"]] = today
    frontmatter[field_map["last_updated"]] = today
    frontmatter[field_map["created_by"]] = "ghostwriter"
    frontmatter[field_map["author"]] = [persona_name]
    frontmatter[field_map["last_updated_by"]] = persona_name

    return render_frontmatter(frontmatter)