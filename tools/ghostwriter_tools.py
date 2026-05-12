import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path.cwd() / "user" / "plugins" / "ghostwriter-for-obsidian"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from gw_core.vault import list_markdown_notes, read_note, vault_status

from gw_core.meta import load_meta_context


ENABLED = True
EMOJI = "🖋️"

AVAILABLE_FUNCTIONS = [
    "ghostwriter_vault_status",
    "ghostwriter_list_notes",
    "ghostwriter_read_note",
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
    }
]


def _json_result(data):
    return json.dumps(data, ensure_ascii=False, indent=2)


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

    return f"Unknown Ghostwriter function: {function_name}", False