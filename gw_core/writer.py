from pathlib import Path
import re
import shutil

from gw_core.commenter import insert_comment_block

from .write_policy import (
    WritePolicy,
    resolve_persona_working_folder,
    reject_workspace_prefixed_path,
    clean_path_input,
    resolve_existing_vault_note_path,
)

from .templates import (
    load_template_frontmatter_for_new_note,
    strip_frontmatter_block,
)
from .governance import (
    sanitise_note_title,
    preprocess_note_update,
    preprocess_contribution,
    apply_ai_frontmatter_updates_to_existing_note,
    apply_mutation_frontmatter_updates,
    preprocess_note_metadata_update,
    preprocess_contribution,
    can_perform_note_action,
)

import logging

logger = logging.getLogger(__name__)

def create_ai_working_folder(vault_root: Path, policy: WritePolicy) -> Path:
    working_folder = resolve_persona_working_folder(vault_root, policy)
    working_folder.mkdir(parents=True, exist_ok=True)
    return working_folder


def ghostwriter_create_folder(
    vault_root: Path,
    policy: WritePolicy,
    folder_path: str,
) -> Path:
    """
    Create a folder inside the active persona's AI workspace only.

    Paths must be relative to the active workspace.
    Do not include _collab/{Persona Name}/.
    """

    if not folder_path or not folder_path.strip():
        raise ValueError("folder_path is required")

    workspace_root = resolve_persona_working_folder(vault_root, policy).resolve()
    vault_root = vault_root.resolve()

    requested = folder_path.strip().replace("\\", "/")

    reject_workspace_prefixed_path(requested)

    workspace_relative = str(
        workspace_root.relative_to(vault_root)
    ).replace("\\", "/")

    target = (workspace_root / requested).resolve()

    try:
        target.relative_to(workspace_root)
    except ValueError:
        raise ValueError(
            f"Folders may only be created inside your workspace: "
            f"{workspace_relative}/"
        )

    if target == workspace_root:
        raise ValueError(
            "Use ghostwriter_create_working_folder for the workspace root."
        )

    if target.exists():
        if target.is_dir():
            return target

        raise ValueError(
            f"A file already exists at {target.relative_to(vault_root)}"
        )

    target.mkdir(parents=True, exist_ok=False)

    return target

def create_blank_note_from_template(
    vault_root: Path,
    policy: WritePolicy,
    note_title: str,
) -> Path:
    working_folder = create_ai_working_folder(vault_root, policy)

    safe_title = sanitise_note_title(note_title)
    note_path = (working_folder / f"{safe_title}.md").resolve()

    if not str(note_path).startswith(str(working_folder)):
        raise PermissionError("Resolved note path is outside the AI working folder")

    if note_path.exists():
        raise FileExistsError(f"Note already exists: {note_path.name}")

    frontmatter_block = load_template_frontmatter_for_new_note(
        vault_root=vault_root,
        persona_name=policy.persona_name,
)

    if frontmatter_block is None:
        note_text = ""
    else:
        note_text = f"{frontmatter_block}\n"

    note_path.write_text(note_text, encoding="utf-8")
    return note_path

def append_to_note(
    vault_root: Path,
    policy: WritePolicy,
    note_path: str,
    content: str,
    frontmatter=None
) -> Path:
    from .write_policy import resolve_owned_note_path
    from .meta import read_meta_ops

    if not content or not content.strip():
        raise ValueError("Append content is required")

    note_path = clean_path_input(note_path)

    target = resolve_existing_vault_note_path(vault_root, note_path)

    if not can_perform_note_action(
        vault_root=vault_root,
        persona=policy.persona_name,
        note_path=note_path,
        action="append",
    ):
        raise PermissionError("Permission denied. Ask the user for permission.")

    meta_ops = read_meta_ops(vault_root)

    existing_text = ""

    if target.exists():
        existing_text = target.read_text(encoding="utf-8")

    updated_text = preprocess_note_update(
        existing_text=existing_text,
        incoming_content=content,
        meta_ops=meta_ops,
        persona_name=policy.persona_name,
        contribution_type="Contribution",
        frontmatter=frontmatter,
    )

    target.write_text(updated_text, encoding="utf-8")

    return target

def comment_on_note(
    vault_root: Path,
    policy: WritePolicy,
    note_path: str,
    anchor: str,
    comment: str,
    position: str = "after",
    block_type: str = "any",
    frontmatter=None,
) -> Path:
    from .write_policy import resolve_owned_note_path
    from .commenter import insert_comment_block
    from .meta import read_meta_ops

    if not comment or not comment.strip():
        raise ValueError("Comment content is required")

    if not anchor or not anchor.strip():
        raise ValueError("Anchor is required")
    
    note_path = clean_path_input(note_path)

    target = resolve_existing_vault_note_path(vault_root, note_path)

    if not can_perform_note_action(
        vault_root=vault_root,
        persona=policy.persona_name,
        note_path=note_path,
        action="comment",
):
        raise PermissionError("Permission denied. Ask the user for permission.")

    if not target.exists():
        raise FileNotFoundError(f"Note not found: {note_path}")

    meta_ops = read_meta_ops(vault_root)

    existing_text = target.read_text(encoding="utf-8")

    existing_text = preprocess_note_metadata_update(
    existing_text=existing_text,
    meta_ops=meta_ops,
    persona_name=policy.persona_name,
    frontmatter=frontmatter,
)

    comment_text = preprocess_contribution(
    content=f"*{comment.strip()}*",
    meta_ops=meta_ops,
    persona_name=policy.persona_name,
    contribution_type="Comment",
).strip()

    updated = insert_comment_block(
    note_text=existing_text,
    anchor=anchor,
    comment_block=comment_text,
    position=position,
    block_type=block_type,
)

    if updated is None:
      raise RuntimeError("Failed to insert comment block")

    updated_text, _match = updated

    target.write_text(updated_text, encoding="utf-8")

    return target

def ghostwriter_move_file(
    vault_root: Path,
    policy: WritePolicy,
    source_path: str,
    destination_path: str,
):
    """
    Move a file inside the active persona workspace only.

    Both source and destination must remain inside:
        _collab/{Persona Name}/
    """

    source_path = clean_path_input(source_path)
    destination_path = clean_path_input(destination_path)

    if not source_path or not source_path.strip():
        raise ValueError("source_path is required")

    if not destination_path or not destination_path.strip():
        raise ValueError("destination_path is required")

    workspace_root = resolve_persona_working_folder(
        vault_root,
        policy
    ).resolve()

    vault_root = vault_root.resolve()

    source_requested = source_path.strip().replace("\\", "/")
    destination_requested = destination_path.strip().replace("\\", "/")

    reject_workspace_prefixed_path(source_requested)
    reject_workspace_prefixed_path(destination_requested)

    source = (workspace_root / source_requested).resolve()
    destination = (workspace_root / destination_requested).resolve()
    workspace_relative = str(
    workspace_root.relative_to(vault_root)
).replace("\\", "/")

    if not workspace_root.exists():
        raise ValueError(
            f"Workspace does not exist for persona_name '{policy.persona_name}': "
            f"{workspace_relative}/"
    )

    # Resolve source
    if source_requested.startswith(f"{workspace_relative}/"):
        source = (vault_root / source_requested).resolve()
    else:
        source = (workspace_root / source_requested).resolve()

    # Resolve destination
    if destination_requested.startswith(f"{workspace_relative}/"):
        destination = (vault_root / destination_requested).resolve()
    else:
        destination = (workspace_root / destination_requested).resolve()

    # Boundary checks
    try:
        source.relative_to(workspace_root)
        destination.relative_to(workspace_root)
    except ValueError:
        raise ValueError(
            f"Files may only be moved inside your workspace: "
            f"{workspace_relative}/"
        )

    # Source validation
    if not source.exists():
        raise ValueError(
            f"Source file does not exist: "
            f"{source.relative_to(vault_root)}"
        )

    if not source.is_file():
        raise ValueError(
            f"Source is not a file: "
            f"{source.relative_to(vault_root)}"
        )

    # Destination validation
    if destination.exists():
        raise ValueError(
            f"Destination already exists: "
            f"{destination.relative_to(vault_root)}"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(str(source), str(destination))

    return {
        "source": str(source.relative_to(vault_root)),
        "destination": str(destination.relative_to(vault_root)),
    }

def resolve_new_note_path(
    vault_root: Path,
    policy: WritePolicy,
    note_path: str,
) -> Path:
    workspace_root = resolve_persona_working_folder(vault_root, policy).resolve()
    vault_root = vault_root.resolve()

    note_path = clean_path_input(note_path)
    requested = note_path.strip().replace("\\", "/")

    reject_workspace_prefixed_path(requested)

    workspace_relative = str(
        workspace_root.relative_to(vault_root)
    ).replace("\\", "/")

    target = (workspace_root / requested).resolve()

    try:
        target.relative_to(workspace_root)
    except ValueError:
        raise ValueError(
            f"Notes may only be created inside your workspace: {workspace_relative}/"
        )

    if target == workspace_root:
        raise ValueError("note_path must point to a note file, not the workspace folder")

    if target.suffix.lower() != ".md":
        target = target.with_suffix(".md")

    if target.exists():
        raise ValueError(f"Note already exists: {target.relative_to(vault_root)}")

    return target

def write_note(
    vault_root: Path,
    policy: WritePolicy,
    note_path: str,
    content: str,
    frontmatter: dict | None = None,
) -> Path:

    from .meta import read_meta_ops
    from .governance import extract_leading_pseudo_frontmatter_chain

    if not note_path or not note_path.strip():
        raise ValueError("note_path is required")

    if not content or not content.strip():
        raise ValueError("content is required")

    meta_ops = read_meta_ops(vault_root)

    pseudo_frontmatter, content = extract_leading_pseudo_frontmatter_chain(
        content=content,
        meta_ops=meta_ops,
    )

    if pseudo_frontmatter:
        frontmatter = {
            **pseudo_frontmatter,
            **(frontmatter or {}),
        }

    target = resolve_new_note_path(vault_root, policy, note_path)

    target.parent.mkdir(parents=True, exist_ok=True)

    frontmatter_block = load_template_frontmatter_for_new_note(
        vault_root=vault_root,
        persona_name=policy.persona_name,
        ai_frontmatter=frontmatter,
    )

    if frontmatter_block is None:
        final_content = strip_frontmatter_block(content).strip()

        if not final_content.endswith("\n"):
            final_content += "\n"
    else:
        clean_body = strip_frontmatter_block(content)
        final_content = f"{frontmatter_block}\n{clean_body.strip()}\n"

    target.write_text(final_content, encoding="utf-8")

    return target