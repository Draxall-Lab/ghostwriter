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