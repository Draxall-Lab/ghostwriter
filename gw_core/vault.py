from pathlib import Path

from .path_utils import normalise_path, safe_relative_path

from .frontmatter import split_frontmatter


META_DIR = "_meta"
META_OPS_FILE = "meta-ops.md"
GUIDE_FOR_AI_FILE = "guide-for-ai.md"


def get_vault_path(settings):
    return normalise_path((settings or {}).get("vault_path", ""))


def vault_status(settings):
    vault_path = get_vault_path(settings)

    if not vault_path:
        return {
            "ok": False,
            "configured": False,
            "vault_path": "",
            "exists": False,
            "is_dir": False,
            "readable": False,
            "meta_dir_found": False,
            "meta_ops_found": False,
            "guide_for_ai_found": False,
            "error": "Vault path is not configured"
        }

    exists = vault_path.exists()
    is_dir = vault_path.is_dir() if exists else False
    readable = False

    if exists and is_dir:
        try:
            next(vault_path.iterdir(), None)
            readable = True
        except Exception:
            readable = False

    meta_dir = vault_path / META_DIR
    meta_ops = meta_dir / META_OPS_FILE
    guide_for_ai = meta_dir / GUIDE_FOR_AI_FILE

    return {
        "ok": exists and is_dir and readable,
        "configured": True,
        "vault_path": str(vault_path),
        "exists": exists,
        "is_dir": is_dir,
        "readable": readable,
        "meta_dir_found": meta_dir.exists() and meta_dir.is_dir(),
        "meta_ops_found": meta_ops.exists() and meta_ops.is_file(),
        "guide_for_ai_found": guide_for_ai.exists() and guide_for_ai.is_file(),
        "error": None if exists and is_dir and readable else "Vault unavailable or not readable"
    }


def list_markdown_notes(settings, include_meta=False):
    status = vault_status(settings)

    if not status["ok"]:
        return {
            "ok": False,
            "error": status["error"],
            "notes": [],
            "count": 0,
            "status": status
        }

    vault_path = get_vault_path(settings)

    if vault_path is None:
      return {
        "ok": False,
        "error": "Vault path unavailable",
        "notes": [],
        "count": 0,
        "status": status
    }
    notes = []

    for path in vault_path.rglob("*.md"):
        try:
            rel = safe_relative_path(vault_path, path)

            if not include_meta and rel.parts and rel.parts[0] == META_DIR:
                continue

            notes.append({
                "path": str(rel).replace("\\", "/"),
                "name": path.name,
                "folder": str(rel.parent).replace("\\", "/") if str(rel.parent) != "." else "",
                "size_bytes": path.stat().st_size,
                "modified": path.stat().st_mtime
            })
        except Exception:
            continue

    notes.sort(key=lambda item: item["path"].lower())

    return {
        "ok": True,
        "notes": notes,
        "count": len(notes),
        "status": status
    }


def read_note(settings, note_path):
    status = vault_status(settings)

    if not status["ok"]:
        return {
            "ok": False,
            "error": status["error"],
            "content": "",
            "status": status
        }

    if not note_path or not str(note_path).strip():
        return {
            "ok": False,
            "error": "No note path provided",
            "content": "",
            "status": status
        }

    vault_path = get_vault_path(settings)

    if vault_path is None:
      return {
        "ok": False,
        "error": "Vault path unavailable",
        "notes": [],
        "count": 0,
        "status": status
    }
    target = (vault_path / str(note_path).strip()).resolve()

    try:
        rel = safe_relative_path(vault_path, target)
    except ValueError as exc:
        return {
            "ok": False,
            "error": str(exc),
            "content": "",
            "status": status
        }

    if not target.exists() or not target.is_file():
        return {
            "ok": False,
            "error": "Note not found",
            "path": str(rel).replace("\\", "/"),
            "content": "",
            "status": status
        }

    if target.suffix.lower() != ".md":
        return {
            "ok": False,
            "error": "Only Markdown files can be read",
            "path": str(rel).replace("\\", "/"),
            "content": "",
            "status": status
        }

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = target.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Failed to read note: {exc}",
            "path": str(rel).replace("\\", "/"),
            "content": "",
            "status": status
        }

    parsed = split_frontmatter(content)

    return {
      "ok": True,
      "path": str(rel).replace("\\", "/"),
      "name": target.name,
      "content": content,
      "body": parsed["body"],
      "has_frontmatter": parsed["has_frontmatter"],
      "frontmatter_raw": parsed["frontmatter_raw"],
      "frontmatter": parsed["frontmatter"],
      "frontmatter_status": parsed["frontmatter_status"],
      "size_bytes": target.stat().st_size,
      "modified": target.stat().st_mtime,
      "status": status
}