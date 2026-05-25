import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path.cwd() / "user" / "plugins" / "ghostwriter-for-obsidian"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from gw_core.vault import get_vault_path, list_markdown_notes, read_note, vault_status
from gw_core.meta import load_meta_context
from gw_core.writer import (
    create_ai_working_folder,
    create_blank_note_from_template,
    append_to_note,
    ghostwriter_create_folder,
    ghostwriter_move_file,
    write_note,
    comment_on_note,
    insert_into_note
)
from gw_core.write_policy import (
    resolve_write_policy,
    resolve_mutation_target_path
)

from gw_core.frontmatter import insert_frontmatter

import logging

logger = logging.getLogger(__name__)


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
    "ghostwriter_create_folder",
    "ghostwriter_move_file",
    "ghostwriter_write_note",
    "ghostwriter_comment_on_note",
    "ghostwriter_insert_into_note",
    "ghostwriter_insert_frontmatter",
    "ghostwriter_check_stream",
    "ghostwriter_check_radar",
    "ghostwriter_add_to_radar"
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
            "description": "Vault-relative path to an existing Markdown note, for example 'Projects/Example.md'. "
                           "Bare filenames are allowed only if they resolve to exactly one note.",
            "parameters": {
                "type": "object",
                "properties": {
                    "persona_name": {
                        "type": "string",
                        "description": "The active persona name. Used for Activity Stream logging."
                    },
                    "path": {
                        "type": "string",
                        "description": "Vault-relative path to the Markdown note, for example 'Projects/Example.md'."
                    }
                },
                "required": ["persona_name","path"]
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
            "description": "Create an empty starter note for later incremental collaboration inside the current AI collaborator's working folder, using Templates/General Note.md frontmatter and populated provenance fields.",
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
        "description": (
            "Append content to the end of an existing Markdown note inside your own Ghostwriter working folder. "
            "This is append-only and does not edit, delete, or replace existing content. "
            "Use the optional frontmatter parameter for metadata suggestions. "
            "Do not include YAML frontmatter inside content."
            "Vault-relative path to an existing Markdown note. "
            "Bare filenames are allowed only if they resolve to exactly one note."
        ),
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
                    "description": (
                        "The content to append to the end of the note. "
                        "Do not include YAML frontmatter here. "
                        "Use the frontmatter parameter for metadata suggestions."
                    )
                },
                "frontmatter": {
                    "type": "object",
                    "description": (
                        "Optional metadata suggestions for the existing note. "
                        "Only fields already present in the note/template and "
                        "not governance-protected may be merged. "
                        "Unknown fields and protected governance fields are ignored."
                    )
                }
            },
            "required": ["persona_name", "note_path", "content"]
        }
    }
},
    {
    "type": "function",
    "is_local": True,
    "function": {
        "name": "ghostwriter_create_folder",
        "description": "Create a folder inside your active AI workspace only.",
        "parameters": {
            "type": "object",
            "properties": {
                "persona_name": {
                    "type": "string",
                    "description": "The active persona name. Used to resolve _collab/{Persona Name}/."
                },
                "folder_path": {
                    "type": "string",
                    "description": "Folder path to create, relative to your workspace or explicitly under _collab/{Persona Name}/."
                }
            },
            "required": ["persona_name", "folder_path"]
        }
    }
},
{
    "type": "function",
    "is_local": True,
    "function": {
        "name": "ghostwriter_move_file",
        "description": "Move a file inside your active AI workspace only.",
        "parameters": {
            "type": "object",
            "properties": {
                "persona_name": {
                    "type": "string",
                    "description": "The active persona name."
                },
                "source_path": {
                    "type": "string",
                    "description": "Source file path."
                },
                "destination_path": {
                    "type": "string",
                    "description": "Destination file path."
                }
            },
            "required": [
                "persona_name",
                "source_path",
                "destination_path"
            ]
        }
    }
},
{
    "type": "function",
    "is_local": True,
    "function": {
        "name": "ghostwriter_write_note",
        "description": (
            "Create and fully write a new Markdown note in a single operation. "
            "Preferred for creating complete notes with content. "
            "Refuses to overwrite existing notes. "
            "Use the optional frontmatter parameter for metadata suggestions. "
            "Do not include YAML frontmatter inside content."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "persona_name": {
                    "type": "string",
                    "description": "The active persona name."
                },
                "note_path": {
                    "type": "string",
                    "description": (
                        "Path of the note to create, relative to your workspace "
                        "or explicitly under _collab/{Persona Name}/."
                    )
                },
                "content": {
                    "type": "string",
                    "description": (
                        "Markdown body content for the new note. "
                        "Do not include YAML frontmatter here. "
                        "Use the frontmatter parameter for metadata suggestions."
                    )
                },
                "frontmatter": {
                    "type": "object",
                    "description": (
                        "Optional metadata suggestions for the new note. "
                        "Only fields already present in the selected template and "
                        "not governance-protected may be merged. "
                        "Unknown fields and protected governance fields are ignored."
                    )
                }
            },
            "required": [
                "persona_name",
                "note_path",
                "content"
            ]
        }
    }
},
{
    "type": "function",
    "is_local": True,
    "function": {
        "name": "ghostwriter_comment_on_note",
        "description": (
            "Add a block-level comment before or after a matched paragraph, heading, list item, or marker in a note. "
            "Does not edit existing text. "
            "Use the optional frontmatter parameter for metadata suggestions. "
            "Do not include YAML frontmatter inside comment."
            "Vault-relative path to an existing Markdown note. "
            "Bare filenames are allowed only if they resolve to exactly one note."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "persona_name": {
                    "type": "string",
                    "description": "The active persona name."
                },
                "note_path": {
                    "type": "string",
                    "description": "Path to the note, relative to your workspace or explicitly under _collab/{Persona Name}/."
                },
                "anchor": {
                    "type": "string",
                    "description": "Text used to identify the target block."
                },
                "comment": {
                    "type": "string",
                    "description": (
                        "The comment/contribution to insert as a separate block. "
                        "Do not include YAML frontmatter here. "
                        "Use the frontmatter parameter for metadata suggestions."
                    )
                },
                "position": {
                    "type": "string",
                    "enum": ["after", "before"],
                    "default": "after"
                },
                "block_type": {
                    "type": "string",
                    "enum": ["paragraph", "heading", "list_item", "marker", "any"],
                    "default": "any"
                },
                "frontmatter": {
                    "type": "object",
                    "description": (
                        "Optional metadata suggestions for the existing note. "
                        "Only fields already present in the note/template and "
                        "not governance-protected may be merged. "
                        "Unknown fields and protected governance fields are ignored."
                    )
                }
            },
            "required": ["persona_name", "note_path", "anchor", "comment"]
        }
    }
},
{
    "type": "function",
    "is_local": True,
    "function": {
        "name": "ghostwriter_insert_into_note",
        "description": (
            "Insert additive body content into an existing governed note at a heading, paragraph, or matched block. "
            "This performs a clean inline body edit without comment formatting. "
            "Vault-relative path to an existing Markdown note. "
            "Bare filenames are allowed only if they resolve to exactly one note."
),
        "parameters": {
            "type": "object",
            "properties": {
                "persona_name": {
                    "type": "string",
                    "description": "The active persona name."
                },
                "note_path": {
                    "type": "string",
                    "description": "Vault-relative path to the note."
                },
                "content": {
                    "type": "string",
                    "description": "The body content to insert. Do not include YAML frontmatter here."
                },
                "anchor": {
                    "type": "string",
                    "description": "Text used to identify the target block."
                },
                "position": {
                    "type": "string",
                    "enum": ["before", "after"],
                    "default": "after"
                },
                "block_type": {
                    "type": "string",
                    "enum": ["paragraph", "heading", "list_item", "marker", "any"],
                    "default": "any"
                },
                "frontmatter": {
                    "type": "object",
                    "description": "Optional metadata suggestions for the existing note."
                }
            },
            "required": ["persona_name", "note_path", "anchor", "content"]
        }
    }
},
{
    "type": "function",
    "is_local": True,
    "function": {
        "name": "ghostwriter_insert_frontmatter",
        "description": (
            "Insert or merge governed frontmatter fields into an existing note "
            "without modifying the body content. "
            "Protected governance fields and unknown fields are ignored."
            "Vault-relative path to an existing Markdown note. "
            "Bare filenames are allowed only if they resolve to exactly one note."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "persona_name": {
                    "type": "string",
                    "description": "The active persona name."
                },
                "note_path": {
                    "type": "string",
                    "description": (
                        "Path to the note, relative to your workspace "
                        "or explicitly under _collab/{Persona Name}/."
                    )
                },
                "frontmatter": {
                    "type": "object",
                    "description": (
                        "Frontmatter fields to merge into the existing note. "
                        "Only fields already present in the note/template and "
                        "not governance-protected may be merged. "
                        "Unknown fields and protected governance fields are ignored."
                    )
                }
            },
            "required": [
                "persona_name",
                "note_path",
                "frontmatter"
            ]
        }
    }
},
{
    "type": "function",
    "is_local": True,
    "function": {
        "name": "ghostwriter_check_stream",
        "description": "Check recent Ghostwriter Activity Stream entries. Optionally filter by persona name.",
        "parameters": {
            "type": "object",
            "properties": {
                "persona_name": {
                    "type": "string",
                    "description": "Optional persona name to filter by. Leave blank for shared recent activity."
                },
                "max_entries": {
                    "type": "integer",
                    "description": "Maximum number of entries to return.",
                    "default": 10
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
        "name": "ghostwriter_check_radar",
        "description": "Check the collaborator Radar note. If Radar.md does not exist for the active collaborator, initialise it using the canonical Radar format.",
        "parameters": {
            "type": "object",
            "properties": {
                "persona_name": {
                    "type": "string",
                    "description": "Optional collaborator persona name. Uses the active collaborator if omitted."
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
        "name": "ghostwriter_add_to_radar",
        "description": "Add or update a note entry in the collaborator Radar note. This places the note in attentional awareness without requiring immediate reading or action.",
        "parameters": {
            "type": "object",
            "properties": {
                "persona_name": {
                    "type": "string",
                    "description": "Optional collaborator persona name. Uses the active collaborator if omitted."
                },
                "note_path": {
                    "type": "string",
                    "description": "The note to add to Radar. Prefer a canonical vault-relative path or Obsidian wikilink."
                },
                "type": {
                    "type": "string",
                    "description": "Where the signal currently sits. Use Active or Peripheral.",
                    "enum": ["Active", "Peripheral"]
                },
                "pull": {
                    "type": "string",
                    "description": "Current attentional force, not objective importance.",
                    "enum": ["faint", "weak", "medium", "strong"]
                },
                "why_it_is_here": {
                    "type": "string",
                    "description": "Brief reason this note belongs on Radar. If user-requested, preserve the user intent."
                }
            },
            "required": ["note_path"]
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

def _ok_data(action, data):
    return {
        "ok": True,
        "action": action,
        "data": data,
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
        try:
            from gw_core.activity_stream import record_activity
            

            persona_name = arguments.get("persona_name", "")
            note_path = arguments.get("path", "")

            if not persona_name:
                raise ValueError("persona_name is required")

            vault_root = get_vault_path(settings)

            target = resolve_mutation_target_path(
                vault_root=vault_root,
                note_path=note_path,
            )

            vault_relative_path = target.relative_to(vault_root).as_posix()

            result = read_note(settings, vault_relative_path)

            if isinstance(result, dict) and result.get("ok") is False:
                return _json_result(result), False

            record_activity(
                vault_root=vault_root,
                persona_name=persona_name,
                activity_type="read",
                note_path=vault_relative_path,
            )

            return _json_result(result), True

        except Exception as exc:
            return _json_result(_error(exc)), False

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
            from gw_core.activity_stream import record_activity

            persona_name = arguments.get("persona_name", "")
            note_path = arguments.get("note_path", "")
            content = arguments.get("content", "")
            frontmatter = arguments.get("frontmatter")

            if frontmatter is None:
                reserved_keys = {
                    "persona_name",
                    "note_path",
                    "content",
                }

                frontmatter = {
                    key: value
                    for key, value in arguments.items()
                    if key not in reserved_keys
                } or None

            if not persona_name:
                raise ValueError("persona_name is required")

            if not note_path:
                raise ValueError("note_path is required")

            if not content:
                raise ValueError("content is required")

            vault_root = get_vault_path(settings)
            policy = resolve_write_policy(vault_root, persona_name)

            target = resolve_mutation_target_path(
                vault_root=vault_root,
                note_path=note_path,
            )

            vault_relative_path = target.relative_to(vault_root).as_posix()

            result = append_to_note(
                vault_root=vault_root,
                policy=policy,
                note_path=vault_relative_path,
                content=content,
                frontmatter=frontmatter,
            )

            if isinstance(result, dict) and result.get("ok") is False:
                return _json_result(result), False

            record_activity(
                vault_root=vault_root,
                persona_name=persona_name,
                activity_type="append",
                note_path=vault_relative_path,
            )
 
            return _json_result(_ok("appended_to_note", result)), True

        except Exception as exc:
            return _json_result(_error(exc)), False
        
    if function_name == "ghostwriter_create_folder":
        try:
            persona_name = arguments.get("persona_name", "")
            folder_path = arguments.get("folder_path", "")

            if not persona_name:
                raise ValueError("persona_name is required")

            if not folder_path:
                raise ValueError("folder_path is required")

            vault_root = get_vault_path(settings)
            policy = resolve_write_policy(vault_root, persona_name)

            created_path = ghostwriter_create_folder(
                vault_root=vault_root,
                policy=policy,
                folder_path=folder_path,
            )

            return _json_result(_ok("created_or_confirmed_folder", created_path)), True

        except Exception as exc:
            return _json_result(_error(exc)), False
        
    if function_name == "ghostwriter_move_file":
        try:
            persona_name = arguments.get("persona_name", "")
            source_path = arguments.get("source_path", "")
            destination_path = arguments.get("destination_path", "")

            if not persona_name:
                raise ValueError("persona_name is required")

            vault_root = get_vault_path(settings)
            policy = resolve_write_policy(vault_root, persona_name)

            result = ghostwriter_move_file(
                vault_root=vault_root,
                policy=policy,
                source_path=source_path,
                destination_path=destination_path,
            )

            return _json_result(_ok("moved_file", result)), True

        except Exception as exc:
            return _json_result(_error(exc)), False
        
    if function_name == "ghostwriter_write_note":

        try:
            from gw_core.activity_stream import record_activity
            
            persona_name = arguments.get("persona_name", "")
            note_path = arguments.get("note_path", "")
            content = arguments.get("content", "")
            frontmatter = arguments.get("frontmatter")

            if frontmatter is None:
                reserved_keys = {
                    "persona_name",
                    "note_path",
                    "content",
                }

                frontmatter = {
                    key: value
                    for key, value in arguments.items()
                    if key not in reserved_keys
                } or None

            if not persona_name:
                raise ValueError("persona_name is required")

            vault_root = get_vault_path(settings)
            policy = resolve_write_policy(vault_root, persona_name)

            result =  write_note(
                vault_root=vault_root,
                policy=policy,
                note_path=note_path,
                content=content,
                frontmatter=frontmatter,
            )

            record_activity(
                vault_root=vault_root,
                persona_name=persona_name,
                activity_type="write",
                note_path=result.relative_to(vault_root).as_posix(),
            )

            return _json_result(_ok("note_written", result)), True

        except Exception as exc:
            return _json_result(_error(exc)), False
        
    if function_name == "ghostwriter_comment_on_note":
        try:
            from gw_core.activity_stream import record_activity
            persona_name = arguments.get("persona_name", "")
            note_path = arguments.get("note_path", "")
            anchor = arguments.get("anchor", "")
            comment = arguments.get("comment", "")
            position = arguments.get("position", "after")
            block_type = arguments.get("block_type", "any")
            frontmatter = arguments.get("frontmatter")

            if frontmatter is None:
                reserved_keys = {
                    "persona_name",
                    "note_path",
                    "anchor",
                    "comment",
                    "position",
                    "block_type",
                }

                frontmatter = {
                    key: value
                    for key, value in arguments.items()
                    if key not in reserved_keys
                } or None

            if not persona_name:
                raise ValueError("persona_name is required")

            vault_root = get_vault_path(settings)
            policy = resolve_write_policy(vault_root, persona_name)

            target = resolve_mutation_target_path(
                vault_root=vault_root,
                note_path=note_path,
            )

            vault_relative_path = target.relative_to(vault_root).as_posix()

            result = comment_on_note(
                vault_root=vault_root,
                policy=policy,
                note_path=vault_relative_path,
                anchor=anchor,
                comment=comment,
                position=position,
                block_type=block_type,
                frontmatter=frontmatter,
            )

            if isinstance(result, dict) and result.get("ok") is False:
                return _json_result(result), False

            record_activity(
                vault_root=vault_root,
                persona_name=persona_name,
                activity_type="comment",
                note_path=vault_relative_path,
            )
 
            return _json_result(_ok("comment_added", result)), True

        except Exception as exc:
            return _json_result(_error(exc)), False
        
    if function_name == "ghostwriter_insert_into_note":
        try:
            from gw_core.activity_stream import record_activity

            persona_name = arguments.get("persona_name", "")
            note_path = arguments.get("note_path", "")
            anchor = arguments.get("anchor", "")
            content = arguments.get("content", "")
            position = arguments.get("position", "after")
            block_type = arguments.get("block_type", "any")
            frontmatter = arguments.get("frontmatter")

            if frontmatter is None:
                reserved_keys = {
                    "persona_name",
                    "note_path",
                    "anchor",
                    "content",
                    "position",
                    "block_type",
                }

                frontmatter = {
                    key: value
                    for key, value in arguments.items()
                    if key not in reserved_keys
                } or None

            if not persona_name:
                raise ValueError("persona_name is required")

            vault_root = get_vault_path(settings)
            policy = resolve_write_policy(vault_root, persona_name)

            target = resolve_mutation_target_path(
                vault_root=vault_root,
                note_path=note_path,
            )

            vault_relative_path = target.relative_to(vault_root).as_posix()

            result = insert_into_note(
                vault_root=vault_root,
                policy=policy,
                note_path=vault_relative_path,
                anchor=anchor,
                content=content,
                position=position,
                block_type=block_type,
                frontmatter=frontmatter,
            )

            if isinstance(result, dict) and result.get("ok") is False:
                return _json_result(result), False

            record_activity(
                vault_root=vault_root,
                persona_name=persona_name,
                activity_type="insert",
                note_path=vault_relative_path,
            )

            return _json_result(_ok("content_inserted", result)), True

        except Exception as exc:
            return _json_result(_error(exc)), False
        
    if function_name == "ghostwriter_insert_frontmatter":
        try:
            from gw_core.activity_stream import record_activity

            persona_name = arguments.get("persona_name", "")
            note_path = arguments.get("note_path", "")
            frontmatter = arguments.get("frontmatter")

            if not persona_name:
                raise ValueError("persona_name is required")

            if not frontmatter:
                reserved_keys = {
                    "persona_name",
                    "note_path",
                }

                frontmatter = {
                    key: value
                    for key, value in arguments.items()
                    if key not in reserved_keys
                } or None

            if not frontmatter:
                raise ValueError("frontmatter is required")

            vault_root = get_vault_path(settings)
            policy = resolve_write_policy(vault_root, persona_name)

            target = resolve_mutation_target_path(
                vault_root=vault_root,
                note_path=note_path,
            )

            vault_relative_path = target.relative_to(vault_root).as_posix()

            result = insert_frontmatter(
                vault_root=vault_root,
                policy=policy,
                note_path=vault_relative_path,
                frontmatter=frontmatter,
            )

            if isinstance(result, dict) and result.get("ok") is False:
                return _json_result(result), False

            record_activity(
                vault_root=vault_root,
                persona_name=persona_name,
                activity_type="frontmatter",
                note_path=vault_relative_path,
            )

            return _json_result(_ok("frontmatter_inserted", result)), True

        except Exception as exc:
            return _json_result(_error(exc)), False
        
    if function_name == "ghostwriter_check_stream":
        try:
            from gw_core.activity_stream import check_stream

            persona_name = arguments.get("persona_name", "")
            max_entries = arguments.get("max_entries", 10)

            try:
                max_entries = int(max_entries)
            except (TypeError, ValueError):
                max_entries = 10

            if max_entries < 1:
                max_entries = 10

            vault_root = get_vault_path(settings)

            entries = check_stream(
                vault_root=vault_root,
                persona_name=persona_name,
                max_entries=max_entries,
            )

            result = {
                "persona_filter": persona_name or "all",
                "count": len(entries),
                "entries": entries,
            }

            return _json_result(_ok_data("activity_stream_checked", result)), True

        except Exception as exc:
            return _json_result(_error(exc)), False
        
    if function_name == "ghostwriter_check_radar":
        try:
            from gw_core.radar import check_radar

            persona_name = arguments.get("persona_name", "")

            vault_root = get_vault_path(settings)

            result = check_radar(
                vault_root=vault_root,
                persona_name=persona_name,
            )

            return _json_result(_ok_data("radar_checked", result)), True

        except Exception as exc:
            return _json_result(_error(exc)), False
        
    if function_name == "ghostwriter_add_to_radar":
        try:
            from gw_core.radar import add_to_radar

            persona_name = arguments.get("persona_name", "")
            note_path = arguments.get("note_path", "")
            signal_type = arguments.get("type", "Active")
            pull = arguments.get("pull", "medium")
            why_it_is_here = arguments.get(
                "why_it_is_here",
                "User requested this note remain on Radar.",
            )

            vault_root = get_vault_path(settings)

            result = add_to_radar(
                vault_root=vault_root,
                persona_name=persona_name,
                note_path=note_path,
                signal_type=signal_type,
                pull=pull,
                why_it_is_here=why_it_is_here,
            )

            return _json_result(_ok_data("radar_updated", result)), True

        except Exception as exc:
            return _json_result(_error(exc)), False