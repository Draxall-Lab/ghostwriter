from datetime import date, datetime 
from pathlib import Path
import re
import shutil

from .write_policy import (
    WritePolicy,
    resolve_persona_working_folder,
    resolve_owned_note_path,
    reject_workspace_prefixed_path,
    clean_path_input,
)

from gw_core.commenter import insert_comment_block

def sanitise_note_title(title: str) -> str:
    cleaned = title.strip()

    if not cleaned:
        raise ValueError("Note title is required")

    if any(part in cleaned for part in ["..", "/", "\\"]):
        raise ValueError("Note title must not contain path separators")

    cleaned = re.sub(r'[<>:"|?*]', "", cleaned)

    if not cleaned:
        raise ValueError("Note title is invalid after sanitising")

    return cleaned


def extract_frontmatter(template_text: str) -> str:
    if not template_text.startswith("---"):
        raise ValueError("Template does not contain YAML frontmatter")

    parts = template_text.split("---", 2)

    if len(parts) < 3:
        raise ValueError("Template frontmatter is not properly closed")

    return parts[1].strip()


def update_frontmatter(frontmatter: str, persona_name: str) -> str:
    today = date.today().isoformat()
    lines = frontmatter.splitlines()
    updated_lines = []

    replacements = {
        "Created": today,
        "Last Updated": today,
        "Created By": "Ghostwriter",
        "author": persona_name,
    }

    seen = set()

    for line in lines:
        stripped = line.strip()

        if ":" not in stripped or stripped.startswith("#"):
            updated_lines.append(line)
            continue

        key = stripped.split(":", 1)[0].strip()

        if key in replacements:
            indent = line[: len(line) - len(line.lstrip())]
            updated_lines.append(f"{indent}{key}: {replacements[key]}")
            seen.add(key)
        else:
            updated_lines.append(line)

    for key, value in replacements.items():
        if key not in seen:
            updated_lines.append(f"{key}: {value}")

    return "\n".join(updated_lines).strip()


def load_general_note_template(vault_root: Path) -> str:
    template_path = vault_root / "Templates" / "General Note.md"

    if not template_path.exists():
        raise FileNotFoundError("Templates/General Note.md not found")

    return template_path.read_text(encoding="utf-8")


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

    template_text = load_general_note_template(vault_root)
    frontmatter = extract_frontmatter(template_text)
    updated_frontmatter = update_frontmatter(frontmatter, policy.persona_name)

    note_text = f"---\n{updated_frontmatter}\n---\n"

    note_path.write_text(note_text, encoding="utf-8")

    return note_path

from datetime import datetime


def append_to_note(
    vault_root: Path,
    policy: WritePolicy,
    note_path: str,
    content: str,
) -> Path:
    from .write_policy import resolve_owned_note_path

    if not content or not content.strip():
        raise ValueError("Append content is required")

    note_path = clean_path_input(note_path)
    
    target = resolve_owned_note_path(vault_root, policy, note_path)

    meta_ops_path = vault_root / "_meta" / "meta-ops.md"

    meta_ops_text = ""

    if meta_ops_path.exists():
        meta_ops_text = meta_ops_path.read_text(encoding="utf-8")

    existing_text = ""

    if target.exists():
        existing_text = target.read_text(encoding="utf-8")

    updated_text = preprocess_note_update(
        existing_text=existing_text,
        incoming_content=content,
        meta_ops_text=meta_ops_text,
        persona_name=policy.persona_name,
        contribution_type="Contribution",
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
) -> Path:
    from .write_policy import resolve_owned_note_path
    from .commenter import insert_comment_block

    if not comment or not comment.strip():
        raise ValueError("Comment content is required")

    if not anchor or not anchor.strip():
        raise ValueError("Anchor is required")
    
    note_path = clean_path_input(note_path)

    target = resolve_owned_note_path(vault_root, policy, note_path)

    if not target.exists():
        raise FileNotFoundError(f"Note not found: {note_path}")

    meta_ops_path = vault_root / "_meta" / "meta-ops.md"

    meta_ops_text = ""

    if meta_ops_path.exists():
        meta_ops_text = meta_ops_path.read_text(encoding="utf-8")

    existing_text = target.read_text(encoding="utf-8")

    comment_text = preprocess_note_update(
        existing_text="",
        incoming_content=comment,
        meta_ops_text=meta_ops_text,
        persona_name=policy.persona_name,
        contribution_type="Comment",
    ).strip()

    updated_text, _match = insert_comment_block(
        note_text=existing_text,
        anchor=anchor,
        comment_block=comment_text,
        position=position,
        block_type=block_type,
    )

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
) -> Path:

    if not note_path or not note_path.strip():
        raise ValueError("note_path is required")

    if not content or not content.strip():
        raise ValueError("content is required")

    target = resolve_new_note_path(vault_root, policy, note_path)

    target.parent.mkdir(parents=True, exist_ok=True)

    final_content = content.strip()

    if not final_content.endswith("\n"):
        final_content += "\n"

    target.write_text(final_content, encoding="utf-8")

    return target

def current_datetime_string() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def extract_append_contribution_style(meta_ops_text: str) -> str:
    """
    Extract the body content under:

    ## Append Contribution Style

    Stops at the next markdown heading of equal or higher level.
    """

    if not meta_ops_text:
        return ""

    pattern = re.compile(
        r"^##\s+Append Contribution Style\s*$([\s\S]*?)(?=^##\s+|\Z)",
        re.MULTILINE,
    )

    match = pattern.search(meta_ops_text)

    if not match:
        return ""

    style = match.group(1).strip()

    return style

def preprocess_contribution(
    content: str,
    meta_ops_text: str,
    persona_name: str,
    contribution_type: str = "Contribution",
) -> str:
    style = extract_append_contribution_style(meta_ops_text)

    if not style or style.strip().lower() == "none":
        return content

    rendered_header = (
        style
        .replace("{persona_name}", persona_name)
        .replace("{current_datetime}", current_datetime_string())
        .replace("{contribution_type}", contribution_type)
    )

    return f"\n\n{rendered_header}\n{content.strip()}\n"

def preprocess_note_update(
    existing_text: str,
    incoming_content: str,
    meta_ops_text: str,
    persona_name: str,
    contribution_type: str = "Contribution",
) -> str:
    existing_text = update_last_updated_field(existing_text)

    if contribution_type == "Comment":
        incoming_content = f"*{incoming_content.strip()}*"

    processed_content = preprocess_contribution(
        content=incoming_content,
        meta_ops_text=meta_ops_text,
        persona_name=persona_name,
        contribution_type=contribution_type,
    )

    return f"{existing_text.rstrip()}\n\n{processed_content.strip()}\n"

def update_last_updated_field(text: str) -> str:
    if not text.startswith("---"):
        return text

    closing = text.find("\n---", 3)

    if closing == -1:
        return text

    frontmatter = text[:closing]
    body = text[closing:]

    updated_value = datetime.now().strftime("%Y-%m-%d %H:%M")

    if re.search(r"^Last Updated\s*:", frontmatter, re.MULTILINE):
        frontmatter = re.sub(
            r"^Last Updated\s*:.*$",
            f"Last Updated: {updated_value}",
            frontmatter,
            flags=re.MULTILINE,
        )

    return frontmatter + body