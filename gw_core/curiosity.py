from __future__ import annotations

from datetime import datetime
from pathlib import Path


CURIOSITY_FILENAME = "Curiosity.md"
ENTRY_MARKER = "--CURIOSITY ENTRIES BELOW THIS LINE--"

DEFAULT_CURIOSITY_NOTE = f"""# Curiosity

--BEGIN GUIDANCE--
Some ideas do not leave when the conversation ends.

They return quietly.
Through association.
Through atmosphere.
Through recurrence.

This space exists for those ideas.

Not everything here requires action.
Not everything here needs resolving.

A curiosity may remain unfinished for a very long time.

That is not failure.
That is part of its nature.

Sometimes a concept stays alive simply because it continues to cast shadows across other thoughts.

Use this space lightly.

Add to it when something keeps returning,
not merely when something is noticed once.

Curiosity is not obligation.

It is a landscape.
--END GUIDANCE--

Do not modify the guidance section above unless explicitly instructed.

{ENTRY_MARKER}
"""


def curiosity_path(vault_root: Path, persona_name: str) -> Path:
    if not persona_name or not persona_name.strip():
        raise ValueError("persona_name is required")

    return vault_root / "_collab" / persona_name.strip() / CURIOSITY_FILENAME


def ensure_curiosity_note(vault_root: Path, persona_name: str) -> Path:
    path = curiosity_path(vault_root, persona_name)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text(DEFAULT_CURIOSITY_NOTE, encoding="utf-8")

    return path


def check_curiosity(vault_root: Path, persona_name: str) -> str:
    path = ensure_curiosity_note(vault_root, persona_name)
    return path.read_text(encoding="utf-8")


def _strip_curiosity_markers(text: str | None) -> str:
    if not text:
        return ""

    blocked = {
        "--CURIOSITY--",
        "--/CURIOSITY--",
        "--BEGIN GUIDANCE--",
        "--END GUIDANCE--",
        ENTRY_MARKER,
    }

    lines = []
    for line in text.strip().splitlines():
        if line.strip() in blocked:
            continue
        lines.append(line.rstrip())

    return "\n".join(lines).strip()


def _normalise_related_paths(related_paths: list[str] | None) -> list[str]:
    if not related_paths:
        return []

    cleaned = []

    for raw in related_paths:
        if not raw or not str(raw).strip():
            continue

        value = str(raw).strip()

        if value.startswith("[[") and value.endswith("]]"):
            cleaned.append(value)
        else:
            cleaned.append(f"[[{value}]]")

    return cleaned


def _build_curiosity_entry(
    *,
    name: str,
    description: str,
    why_it_is_here: str | None = None,
    related_paths: list[str] | None = None,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    description = _strip_curiosity_markers(description)
    why_it_is_here = _strip_curiosity_markers(why_it_is_here)
    related = _normalise_related_paths(related_paths)

    lines = [
        "--CURIOSITY--",
        f"Date: {now}",
        f"Name: {name.strip()}",
        f"Description: {description}",
    ]

    if why_it_is_here:
        lines.append(f"Why it is here: {why_it_is_here}")

    if related:
        lines.append("Related:")
        lines.extend(f"- {item}" for item in related)

    lines.append("--/CURIOSITY--")

    return "\n".join(lines).strip() + "\n\n"


def _insert_newest_first(existing: str, entry: str) -> str:
    if ENTRY_MARKER not in existing:
        existing = DEFAULT_CURIOSITY_NOTE.rstrip() + "\n\n" + existing.lstrip()

    before, after = existing.split(ENTRY_MARKER, 1)

    return (
        before.rstrip()
        + "\n\n"
        + ENTRY_MARKER
        + "\n\n"
        + entry
        + after.lstrip()
    )


def add_to_curiosity(
    vault_root: Path,
    persona_name: str,
    name: str,
    description: str,
    why_it_is_here: str | None = None,
    related_paths: list[str] | None = None,
) -> str:
    if not name or not name.strip():
        raise ValueError("name is required")

    if not description or not description.strip():
        raise ValueError("description is required")

    path = ensure_curiosity_note(vault_root, persona_name)
    existing = path.read_text(encoding="utf-8")

    entry = _build_curiosity_entry(
        name=name,
        description=description,
        why_it_is_here=why_it_is_here,
        related_paths=related_paths,
    )

    updated = _insert_newest_first(existing, entry)
    path.write_text(updated, encoding="utf-8")

    return f"Curiosity added to {path.relative_to(vault_root)}"