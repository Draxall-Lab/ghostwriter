from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class WritePolicy:
    allowed_root: str
    persona_name: str


def cache_check():
    """
    Future hook for cached meta-ops policy resolution.

    For now, meta-ops remains authoritative on every call.
    """
    return None

def clean_path_input(value: str) -> str:
    value = value.strip()

    # Remove accidental markdown emphasis wrapping
    if value.startswith("_") and value.endswith("_"):
        value = value[1:-1]

    if value.startswith("*") and value.endswith("*"):
        value = value[1:-1]

    return value.strip()

def normalise_workspace_relative_path(path: str, policy: WritePolicy) -> str:
    value = clean_path_input(path)

    value = value.replace("\\", "/").strip()

    workspace_prefix = f"_collab/{policy.persona_name}/"

    if value.startswith(workspace_prefix):
        value = value[len(workspace_prefix):]

    if value.startswith("_collab/"):
        raise ValueError(
            "Write paths may only target your own workspace."
        )

    if value.startswith("/") or ".." in value.split("/"):
        raise ValueError("Invalid workspace-relative path.")

    return value.strip("/")

def normalise_persona_name(persona_name: str) -> str:
    cleaned = persona_name.strip()

    if not cleaned:
        raise ValueError("Persona name is required")

    if any(part in cleaned for part in ["..", "/", "\\"]):
        raise ValueError("Persona name must not contain path separators")

    cleaned = re.sub(r'[<>:"|?*]', "", cleaned)

    if not cleaned:
        raise ValueError("Persona name is invalid after sanitising")

    return cleaned


def load_meta_ops(vault_root: Path) -> str:
    meta_ops_path = vault_root / "_meta" / "meta-ops.md"

    if not meta_ops_path.exists():
        raise FileNotFoundError("_meta/meta-ops.md not found")

    return meta_ops_path.read_text(encoding="utf-8")

def reject_workspace_prefixed_path(path_value: str) -> None:
    requested = (path_value or "").strip().replace("\\", "/").lstrip("/")

    lowered = requested.lower()

    if lowered == "_collab" or lowered.startswith("_collab/"):
        raise ValueError(
            "Use paths relative to your workspace. "
            "Do not include _collab/{Persona Name}/ in tool paths."
        )

def resolve_write_policy(vault_root: Path, persona_name: str) -> WritePolicy:
    cached = cache_check()
    if cached:
        return cached

    meta_ops = load_meta_ops(vault_root)

    # Stage 1 deliberately keeps this simple:
    # meta-ops must explicitly authorise _collab as the working area.
    if "_collab/" not in meta_ops and "`_collab/`" not in meta_ops:
        raise PermissionError("meta-ops does not authorise _collab/ as a collaboration zone")

    persona = normalise_persona_name(persona_name)

    return WritePolicy(
        allowed_root="_collab",
        persona_name=persona,
    )


def resolve_persona_working_folder(vault_root: Path, policy: WritePolicy) -> Path:
    root = (vault_root / policy.allowed_root).resolve()
    target = (root / policy.persona_name).resolve()

    if not str(target).startswith(str(root)):
        raise PermissionError("Resolved working folder is outside the allowed collaboration root")

    return target

def resolve_owned_note_path(vault_root: Path, policy: WritePolicy, note_path: str) -> Path:
    if not note_path or not note_path.strip():
        raise ValueError("note_path is required")

    requested = note_path.strip().replace("\\", "/")

    requested = normalise_workspace_relative_path(requested, policy)
    # reject_workspace_prefixed_path(requested)

    if requested.startswith("/"):
        raise PermissionError("Absolute paths are not allowed")

    if ".." in Path(requested).parts:
        raise PermissionError("Path traversal is not allowed")

    working_folder = resolve_persona_working_folder(vault_root, policy).resolve()
    vault_root = vault_root.resolve()

    target = (working_folder / requested).resolve()

    try:
        target.relative_to(working_folder)
    except ValueError:
        raise PermissionError("Append target must be inside your own working folder")

    if target.suffix.lower() != ".md":
        raise ValueError("Append target must be a Markdown note")

    if not target.exists():
        raise FileNotFoundError(f"Note not found: {requested}")

    return target

def resolve_existing_vault_note_path(
    vault_root: Path,
    note_path: str,
) -> Path:
    if not note_path or not note_path.strip():
        raise ValueError("note_path is required")

    requested = note_path.strip().replace("\\", "/")

    if requested.startswith("/"):
        raise PermissionError("Absolute paths are not allowed")

    if ".." in Path(requested).parts:
        raise PermissionError("Path traversal is not allowed")

    vault_root = vault_root.resolve()
    target = (vault_root / requested).resolve()

    try:
        target.relative_to(vault_root)
    except ValueError:
        raise PermissionError("Note path must stay inside the vault")

    if target.suffix.lower() != ".md":
        raise ValueError("Target must be a Markdown note")

    if not target.exists():
        raise FileNotFoundError(f"Note not found: {requested}")

    return target