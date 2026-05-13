from datetime import date
from pathlib import Path
import re

from .write_policy import WritePolicy, resolve_persona_working_folder


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

    target = resolve_owned_note_path(vault_root, policy, note_path)

    contribution = f"\n\n{content.strip()}\n"

    with target.open("a", encoding="utf-8") as handle:
        handle.write(contribution)

    return target