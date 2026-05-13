from pathlib import Path

from gw_core.vault import get_vault_path
from gw_core.write_policy import resolve_write_policy
from gw_core.writer import create_ai_working_folder, create_blank_note_from_template


def _ok(action: str, path: Path, policy_source: str = "_meta/meta-ops.md"):
    return {
        "ok": True,
        "action": action,
        "path": str(path),
        "policy_source": policy_source,
    }


def _error(exc: Exception):
    return {
        "ok": False,
        "error": type(exc).__name__,
        "message": str(exc),
    }


def create_folder(path_params=None, body=None, settings=None):
    try:
        body = body or {}

        persona_name = body.get("persona_name") or body.get("author")
        if not persona_name:
            raise ValueError("persona_name is required")

        vault_root = Path(get_vault_path(settings))
        policy = resolve_write_policy(vault_root, persona_name)

        folder_path = create_ai_working_folder(vault_root, policy)

        return _ok("created_or_confirmed_working_folder", folder_path)

    except Exception as exc:
        return _error(exc)


def create_note(path_params=None, body=None, settings=None):
    try:
        body = body or {}

        persona_name = body.get("persona_name") or body.get("author")
        note_title = body.get("note_title") or body.get("title")

        if not persona_name:
            raise ValueError("persona_name is required")

        if not note_title:
            raise ValueError("note_title is required")

        vault_root = get_vault_path(settings)
        policy = resolve_write_policy(vault_root, persona_name)

        note_path = create_blank_note_from_template(
            vault_root=vault_root,
            policy=policy,
            note_title=note_title,
        )

        return _ok("created_blank_note", note_path)

    except Exception as exc:
        return _error(exc)