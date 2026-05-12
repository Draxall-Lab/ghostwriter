import hashlib
from pathlib import Path
from typing import Any

from .frontmatter import split_frontmatter
from .vault import get_vault_path, vault_status


META_DIR = "_meta"
GUIDE_FOR_AI_FILE = "guide-for-ai.md"
META_OPS_FILE = "meta-ops.md"


def file_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def extract_markdown_sections(body: str) -> dict[str, str]:
    """
    Extract Markdown heading sections.

    Returns:
    {
        "Purpose": "section text...",
        "Core Instructions": "section text..."
    }
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
                "error": None
            },
            "sections": {},
            "hash": None,
            "modified": None,
            "size_bytes": 0
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
                "error": None
            },
            "sections": {},
            "hash": None,
            "modified": None,
            "size_bytes": 0
        }

    parsed = split_frontmatter(content)
    body = parsed["body"]

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
        "sections": extract_markdown_sections(body),
        "hash": file_sha256(content),
        "modified": path.stat().st_mtime,
        "size_bytes": path.stat().st_size
    }


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
            "meta_ops": None
        }

    vault_path = get_vault_path(settings)

    if vault_path is None:
        return {
            "ok": False,
            "error": "Vault path unavailable",
            "status": status,
            "guide_for_ai": None,
            "meta_ops": None
        }

    guide = read_meta_file(vault_path, GUIDE_FOR_AI_FILE)
    meta_ops = read_meta_file(vault_path, META_OPS_FILE)

    return {
        "ok": guide.get("ok", False) and meta_ops.get("ok", False),
        "error": None if guide.get("ok") and meta_ops.get("ok") else "One or more meta files could not be loaded",
        "status": status,
        "guide_for_ai": guide,
        "meta_ops": meta_ops,
        "summary": build_meta_summary(guide, meta_ops)
    }


def build_meta_summary(guide: dict[str, Any], meta_ops: dict[str, Any]) -> dict[str, Any]:
    return {
        "guide_loaded": bool(guide.get("ok")),
        "meta_ops_loaded": bool(meta_ops.get("ok")),
        "guide_sections": list((guide.get("sections") or {}).keys()),
        "meta_ops_sections": list((meta_ops.get("sections") or {}).keys()),
        "guide_hash": guide.get("hash"),
        "meta_ops_hash": meta_ops.get("hash")
    }