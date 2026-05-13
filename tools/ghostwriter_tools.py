import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path.cwd() / "user" / "plugins" / "ghostwriter-for-obsidian"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from gw_core.vault import get_vault_path, list_markdown_notes, read_note, vault_status
from gw_core.meta import load_meta_context
from gw_core.write_policy import resolve_write_policy
from gw_core.writer import (
    create_ai_working_folder,
    create_blank_note_from_template,
    append_to_note,
)


ENABLED = True
EMOJI = "🖋️"

AVAILABLE_FUNCTIONS = [
    "ghostwriter_vault_status",
    "ghostwriter_list_notes",
    "ghostwriter_read_note",
    "ghostwriter_load_meta_context",
    "ghostwriter_create_working_folder",
    "ghostwriter_create_blank_note",
    "ghostwriter_append_to_note",
]

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "ghostwriter_vault_status",
            "description": "Check whether the configured Obsidian vault is reachable and whether Ghostwriter meta files are present.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "ghostwriter_list_notes",
            "description": "List Markdown notes in the configured Obsidian vault. By default, Ghostwriter hides the internal _meta folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_meta": {
                        "type": "boolean",
                        "description": "Whether to include notes from the internal _meta folder. Defaults to false."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "ghostwriter_read_note",
            "description": "Read a specific Markdown note from the configured Obsidian vault using its vault-relative path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Vault-relative path to the Markdown note, for example 'Projects/Example.md'."
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "ghostwriter_load_meta_context",
            "description": "Load Ghostwriter's operational meta context from _meta/guide-for-ai.md and _meta/meta-ops.md, including frontmatter and Markdown sections.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "ghostwriter_create_working_folder",
            "description": "Create or confirm the current AI collaborator's working folder inside the meta-ops-approved collaboration zone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "persona_name": {
                        "type": "string",
                        "description": "The AI collaborator/persona name to use for the working folder."
                    }
                },
                "required": ["persona_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "ghostwriter_create_blank_note",
            "description": "Create a blank Markdown note inside the current AI collaborator's working folder, using Templates/General Note.md frontmatter and populated provenance fields.",
            "parameters": {
                "type": "object",
                "properties": {
                    "persona_name": {
                        "type": "string",
                        "description": "The AI collaborator/persona name to use as the note author and working folder name."
                    },
                    "note_title": {
                        "type": "string",
                        "description": "The title of the note to create. The note will be created as a Markdown file."
                    }
                },
                "required": ["persona_name", "note_title"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "ghostwriter_append_to_note",
            "description": "Append content to the end of an existing Markdown note inside your own Ghostwriter working folder. This is append-only and does not edit, delete, or replace existing content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "persona_name": {
                        "type": "string",
                        "description": "The AI collaborator/persona name. This must match your own collaborator identity."
                    },
                    "note_path": {
                        "type": "string",
                        "description": "Vault-relative path to the Markdown note inside your own working folder, for example '_collab/Alfred/Test Note.md'."
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to append to the end of the note."
                    }
                },
                "required": ["persona_name", "note_path", "content"]
            }
        }
    }
]


def _json_result(data):
    return json.dumps(data, ensure_ascii=False, indent=2)


def _ok(action, path):
    return {
        "ok": True,
        "action": action,
        "path": str(path),
        "policy_source": "_meta/meta-ops.md",
    }


def _error(exc):
    return {
        "ok": False,
        "error": type(exc).__name__,
        "message": str(exc),
    }


def execute(function_name, arguments, config=None, plugin_settings=None):
    arguments = arguments or {}
    settings = plugin_settings or {}

    if function_name == "ghostwriter_vault_status":
        return _json_result(vault_status(settings)), True

    if function_name == "ghostwriter_list_notes":
        include_meta = bool(arguments.get("include_meta", False))
        return _json_result(list_markdown_notes(settings, include_meta=include_meta)), True

    if function_name == "ghostwriter_read_note":
        note_path = arguments.get("path", "")
        return _json_result(read_note(settings, note_path)), True

    if function_name == "ghostwriter_load_meta_context":
        return _json_result(load_meta_context(settings)), True

    if function_name == "ghostwriter_create_working_folder":
        try:
            persona_name = arguments.get("persona_name", "")

            if not persona_name:
                raise ValueError("persona_name is required")

            vault_root = get_vault_path(settings)
            policy = resolve_write_policy(vault_root, persona_name)
            folder_path = create_ai_working_folder(vault_root, policy)

            return _json_result(_ok("created_or_confirmed_working_folder", folder_path)), True

        except Exception as exc:
            return _json_result(_error(exc)), False

    if function_name == "ghostwriter_create_blank_note":
        try:
            persona_name = arguments.get("persona_name", "")
            note_title = arguments.get("note_title", "")

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

            return _json_result(_ok("created_blank_note", note_path)), True

        except Exception as exc:
            return _json_result(_error(exc)), False
        
    if function_name == "ghostwriter_append_to_note":
        try:
            persona_name = arguments.get("persona_name", "")
            note_path = arguments.get("note_path", "")
            content = arguments.get("content", "")

            if not persona_name:
                raise ValueError("persona_name is required")

            if not note_path:
                raise ValueError("note_path is required")

            if not content:
                raise ValueError("content is required")

            vault_root = get_vault_path(settings)
            policy = resolve_write_policy(vault_root, persona_name)

            appended_path = append_to_note(
                vault_root=vault_root,
                policy=policy,
                note_path=note_path,
                content=content,
            )

            return _json_result(_ok("appended_to_note", appended_path)), True

        except Exception as exc:
            return _json_result(_error(exc)), False

    return f"Unknown Ghostwriter function: {function_name}", False