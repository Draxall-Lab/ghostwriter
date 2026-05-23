from dataclasses import dataclass
from pathlib import Path
import re

from .activity_stream import normalise_stream_path


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

def resolve_existing_note_path(vault_root: Path, note_path: str) -> Path:
    """
    Resolve an existing Markdown note safely.

    Rules:
    - Vault-relative paths are accepted directly.
    - Bare filenames are searched across the vault.
    - Bare filename search must resolve to exactly one match.
    - Missing notes are never created here.
    - Ambiguous filenames raise with candidate paths.
    """
    if not note_path or not note_path.strip():
        raise ValueError("note_path is required")

    raw = note_path.strip().replace("\\", "/").lstrip("/")

    if not raw.endswith(".md"):
        raw += ".md"

    if ".." in Path(raw).parts:
        raise ValueError("note_path must not contain '..'")

    # Vault-relative path
    if "/" in raw:
        target = (vault_root / raw).resolve()

        try:
            target.relative_to(vault_root.resolve())
        except ValueError:
            raise ValueError("note_path must stay inside the vault")

        if not target.exists():
            raise FileNotFoundError(f"Note not found: {raw}")

        if not target.is_file():
            raise ValueError(f"Path is not a file: {raw}")

        return target

    # Bare filename lookup
    matches = [
        path
        for path in vault_root.rglob(raw)
        if path.is_file() and path.suffix == ".md"
    ]

    if len(matches) == 1:
        return matches[0]

    if not matches:
        raise FileNotFoundError(
            f"Note not found by filename: {raw}. Use a vault-relative path."
        )

    options = "\n".join(
        f"- {path.relative_to(vault_root).as_posix()}"
        for path in matches[:10]
    )

    raise ValueError(
        f"Ambiguous note filename: {raw}\n"
        f"Use a vault-relative path such as:\n{options}"
    )

def resolve_mutation_target_path(vault_root: Path, note_path: str) -> Path:
    raw = normalise_stream_path(note_path)

    if not raw:
        raise ValueError("note_path is required")

    # 1. Exact vault-relative path
    exact = vault_root / raw
    if exact.exists() and exact.is_file() and exact.suffix == ".md":
        return exact

    # 2. Add .md if omitted and try exact path again
    if not raw.endswith(".md"):
        exact_md = vault_root / f"{raw}.md"
        if exact_md.exists() and exact_md.is_file():
            return exact_md

    wanted_filename = raw if raw.endswith(".md") else f"{raw}.md"
    wanted_title = raw.removesuffix(".md").lower()

    matches: list[Path] = []

    for path in vault_root.rglob("*.md"):
        rel = path.relative_to(vault_root).as_posix()

        # Optional: skip system/internal notes if you want
        if rel.startswith("_ghostwriter/"):
            continue

        filename_match = path.name.lower() == wanted_filename.lower()
        title_match = path.stem.lower() == wanted_title

        if filename_match or title_match:
            matches.append(path)

    if not matches:
        raise FileNotFoundError(f"No existing note found for: {note_path}")

    if len(matches) > 1:
        options = "\n".join(
            f"- {p.relative_to(vault_root).as_posix()}" for p in matches
        )
        raise ValueError(
            f"Ambiguous note reference: {note_path}\n"
            f"Matched multiple notes:\n{options}"
        )

    return matches[0]