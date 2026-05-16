import hashlib
import re
from pathlib import Path
from typing import Any

from .frontmatter import split_frontmatter
from .vault import get_vault_path, vault_status


META_DIR = "_meta"
GUIDE_FOR_AI_FILE = "guide-for-ai.md"
META_OPS_FILE = "meta-ops.md"

SECTION_START = "--SECTION--"
SECTION_END = "--/SECTION--"


def file_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def normalise_section_key(name: str) -> str:
    """
    Convert human-readable section names into stable lookup keys.

    Example:
        "Template Path" -> "template_path"
        "AI Working Folders" -> "ai_working_folders"
    """
    key = name.strip().lower()
    key = re.sub(r"[^a-z0-9]+", "_", key)
    return key.strip("_")


def extract_markdown_sections(body: str) -> dict[str, str]:
    """
    Legacy Markdown heading extraction.

    Kept for guide-for-ai.md and any older non-block meta files.
    """

    sections: dict[str, list[str]] = {}
    current_heading = None

    for line in body.splitlines():
        stripped = line.strip()

        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()

            if heading:
                current_heading = heading
                sections.setdefault(current_heading, [])

            continue

        if current_heading:
            sections[current_heading].append(line)

    return {
        heading: "\n".join(lines).strip()
        for heading, lines in sections.items()
    }


def extract_meta_sections(body: str) -> dict[str, Any]:
    """
    Extract canonical Ghostwriter meta-ops section blocks.

    Expected block shape:

    --SECTION--
    ## Name: Section Name

    Description:
    Human-readable context.

    Section_Directive:
    Operational instruction/configuration.

    --/SECTION--

    Returns:
    {
        "sections": {
            "section_name": {
                "name": "Section Name",
                "description": "...",
                "directive": "...",
                "raw": "...",
            }
        },
        "warnings": [...]
    }
    """

    sections: dict[str, dict[str, str]] = {}
    warnings: list[str] = []

    block_pattern = re.compile(
        rf"{re.escape(SECTION_START)}(.*?){re.escape(SECTION_END)}",
        re.DOTALL,
    )

    blocks = list(block_pattern.finditer(body))

    start_count = body.count(SECTION_START)
    end_count = body.count(SECTION_END)

    if start_count != end_count:
        warnings.append(
            f"Section marker mismatch: found {start_count} start marker(s) and {end_count} end marker(s)"
        )

    for index, match in enumerate(blocks, start=1):
        raw_inner = match.group(1).strip()
        raw_block = match.group(0).strip()

        name_match = re.search(
            r"^\s*##\s+Name:\s*(.+?)\s*$",
            raw_inner,
            re.MULTILINE,
        )

        if not name_match:
            warnings.append(f"Section block {index} is missing a valid '## Name:' heading")
            continue

        name = name_match.group(1).strip()
        key = normalise_section_key(name)

        if not key:
            warnings.append(f"Section block {index} has an empty or invalid section name")
            continue

        if key in sections:
            warnings.append(f"Duplicate section name ignored: {name}")
            continue

        description = ""
        directive = ""

        description_match = re.search(
            r"Description:\s*(.*?)(?=\n\s*Section_Directive:|\Z)",
            raw_inner,
            re.DOTALL,
        )

        if description_match:
            description = description_match.group(1).strip()
        else:
            warnings.append(f"Section '{name}' is missing a Description field")

        directive_match = re.search(
            r"Section_Directive:\s*(.*)\Z",
            raw_inner,
            re.DOTALL,
        )

        if directive_match:
            directive = directive_match.group(1).strip()
        else:
            warnings.append(f"Section '{name}' is missing a Section_Directive field")

        if not directive:
            warnings.append(f"Section '{name}' has an empty Section_Directive")

        sections[key] = {
            "name": name,
            "description": description,
            "directive": directive,
            "raw": raw_block,
        }

    if start_count > 0 and not blocks:
        warnings.append("Section markers were found, but no complete section blocks could be parsed")

    return {
        "sections": sections,
        "warnings": warnings,
    }

def get_meta_section_directive(
    meta_context: dict[str, Any],
    section_key: str,
) -> str | None:
    """
    Retrieve a Section_Directive value from parsed meta-ops sections.

    Example:
        get_meta_section_directive(context["meta_ops"], "template_path")

    Returns:
        The directive string if found and non-empty,
        otherwise None.
    """

    if not meta_context:
        return None

    sections = meta_context.get("sections")

    if not isinstance(sections, dict):
        return None

    section = sections.get(section_key)

    if not isinstance(section, dict):
        return None

    directive = section.get("directive")

    if not isinstance(directive, str):
        return None

    directive = directive.strip()

    return directive or None


def read_meta_file(vault_path: Path, filename: str) -> dict[str, Any]:
    path = vault_path / META_DIR / filename
    rel_path = f"{META_DIR}/{filename}"

    if not path.exists() or not path.is_file():
        return {
            "ok": False,
            "path": rel_path,
            "exists": False,
            "error": f"{rel_path} not found",
            "content": "",
            "body": "",
            "frontmatter": {},
            "frontmatter_status": {
                "present": False,
                "parsed": False,
                "error": None,
            },
            "sections": {},
            "section_warnings": [],
            "hash": None,
            "modified": None,
            "size_bytes": 0,
        }

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return {
            "ok": False,
            "path": rel_path,
            "exists": True,
            "error": f"Failed to read {rel_path}: {exc}",
            "content": "",
            "body": "",
            "frontmatter": {},
            "frontmatter_status": {
                "present": False,
                "parsed": False,
                "error": None,
            },
            "sections": {},
            "section_warnings": [],
            "hash": None,
            "modified": None,
            "size_bytes": 0,
        }

    parsed = split_frontmatter(content)
    body = parsed["body"]

    if filename == META_OPS_FILE:
        section_result = extract_meta_sections(body)
        sections = section_result["sections"]
        section_warnings = section_result["warnings"]
    else:
        sections = extract_markdown_sections(body)
        section_warnings = []

    return {
        "ok": True,
        "path": rel_path,
        "exists": True,
        "error": None,
        "content": content,
        "body": body,
        "has_frontmatter": parsed["has_frontmatter"],
        "frontmatter_raw": parsed["frontmatter_raw"],
        "frontmatter": parsed["frontmatter"],
        "frontmatter_status": parsed["frontmatter_status"],
        "sections": sections,
        "section_warnings": section_warnings,
        "hash": file_sha256(content),
        "modified": path.stat().st_mtime,
        "size_bytes": path.stat().st_size,
    }

def read_meta_ops(vault_root: Path) -> dict[str, Any]:
    """
    Convenience helper for loading parsed meta-ops.md directly
    from a resolved vault root.
    """

    return read_meta_file(vault_root, META_OPS_FILE)

def load_meta_context(settings: dict | None = None) -> dict[str, Any]:
    """
    Load Ghostwriter operational meta context fresh from disk.

    This intentionally does not cache yet.
    """

    settings = settings or {}
    status = vault_status(settings)

    if not status.get("ok"):
        return {
            "ok": False,
            "error": status.get("error") or "Vault unavailable",
            "status": status,
            "guide_for_ai": None,
            "meta_ops": None,
        }

    vault_path = get_vault_path(settings)

    if vault_path is None:
        return {
            "ok": False,
            "error": "Vault path unavailable",
            "status": status,
            "guide_for_ai": None,
            "meta_ops": None,
        }

    guide = read_meta_file(vault_path, GUIDE_FOR_AI_FILE)
    meta_ops = read_meta_file(vault_path, META_OPS_FILE)

    return {
        "ok": guide.get("ok", False) and meta_ops.get("ok", False),
        "error": None if guide.get("ok") and meta_ops.get("ok") else "One or more meta files could not be loaded",
        "status": status,
        "guide_for_ai": guide,
        "meta_ops": meta_ops,
        "summary": build_meta_summary(guide, meta_ops),
    }


def build_meta_summary(guide: dict[str, Any], meta_ops: dict[str, Any]) -> dict[str, Any]:
    return {
        "guide_loaded": bool(guide.get("ok")),
        "meta_ops_loaded": bool(meta_ops.get("ok")),
        "guide_sections": list((guide.get("sections") or {}).keys()),
        "meta_ops_sections": list((meta_ops.get("sections") or {}).keys()),
        "meta_ops_section_warnings": meta_ops.get("section_warnings") or [],
        "guide_hash": guide.get("hash"),
        "meta_ops_hash": meta_ops.get("hash"),
    }