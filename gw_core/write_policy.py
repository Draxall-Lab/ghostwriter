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

    if note_path.startswith("/") or note_path.startswith("\\"):
        raise PermissionError("Absolute paths are not allowed")

    if ".." in Path(note_path).parts:
        raise PermissionError("Path traversal is not allowed")

    working_folder = resolve_persona_working_folder(vault_root, policy).resolve()
    target = (vault_root / note_path).resolve()

    if not str(target).startswith(str(working_folder)):
        raise PermissionError("Append target must be inside your own working folder")

    if target.suffix.lower() != ".md":
        raise ValueError("Append target must be a Markdown note")

    if not target.exists():
        raise FileNotFoundError(f"Note not found: {note_path}")

    return target