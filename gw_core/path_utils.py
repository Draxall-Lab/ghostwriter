from pathlib import Path


def normalise_path(path_value):
    if not path_value or not str(path_value).strip():
        return None

    try:
        return Path(str(path_value).strip()).expanduser().resolve()
    except Exception:
        return Path(str(path_value).strip()).expanduser()


def safe_relative_path(vault_path, target_path):
    vault = Path(vault_path).resolve()
    target = Path(target_path).resolve()

    try:
        return target.relative_to(vault)
    except ValueError:
        raise ValueError("Requested path is outside the configured vault")
    
def resolve_existing_vault_note_path(
    vault_root: Path,
    path: str,
) -> Path:

    if not path:
        raise ValueError("Path is required.")

    candidate = (vault_root / path).resolve()
    root = vault_root.resolve()

    if not str(candidate).startswith(str(root)):
        raise ValueError("Path escapes vault root.")

    if candidate.suffix.lower() != ".md":
        raise ValueError("Only Markdown notes can be edited.")

    if not candidate.exists():
        raise FileNotFoundError(candidate)

    return candidate