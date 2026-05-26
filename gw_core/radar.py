from pathlib import Path
from datetime import datetime
import re

RADAR_FILENAME = "Radar.md"

RADAR_TEMPLATE = """---
type:
  - system
  - radar
created by: Ghostwriter
---

# Radar

--BEGIN GUIDANCE--
Guidance for you and how to use this Radar note:

Radar.md is a lightweight attentional surface for ongoing conceptual pull.

It is not a task list, priority queue, or memory database.

You may freely add, update, cool, move, or remove entries depending on:
- current curiosity
- conceptual recurrence
- unresolved tension
- structural proximity
- resurfacing relevance
- changing attentional pull

When adding or updating Radar entries, prefer using the dedicated Radar tools rather than standard append operations.

Pull describes current attentional force, not objective importance.

Recommended pull values:
- faint
- weak
- medium
- strong

Type describes where the signal currently sits:
- Active
- Peripheral

Use canonical vault-relative wikilink paths.

Example:

[[_collab/Evelyn/philosophy/Digital Hauntology]]

Do not use shortened title-only wikilinks unless explicitly instructed.

When attention feels quiet or unresolved, you may occasionally explore nearby notes
or recent activity to see whether anything naturally stands out.

Leave a single blank line between Radar entries for readability.

You must add entries strictly using this format:

--RADAR--
Note: [[Path to note]]

Type:
Pull:
Why it is here:
Last Noticed:
--/RADAR--

--END GUIDANCE--

Do not modify the guidance section above unless explicitly instructed.

--RADAR ENTRIES BELOW THIS LINE--

"""

RADAR_ENTRIES_ANCHOR = "--RADAR ENTRIES BELOW THIS LINE--"
RADAR_START = "--RADAR--"
RADAR_END = "--/RADAR--"

VALID_RADAR_TYPES = {"active", "peripheral"}
VALID_PULL_VALUES = {"faint", "weak", "medium", "strong"}

def get_radar_path(
    vault_root: Path,
    persona_name: str,
) -> Path:
    return (
        vault_root
        / "_collab"
        / persona_name
        / RADAR_FILENAME
    )


def ensure_radar_note(
    vault_root: Path,
    persona_name: str,
) -> Path:
    path = get_radar_path(vault_root, persona_name)

    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text(RADAR_TEMPLATE, encoding="utf-8")

    return path


def check_radar(
    vault_root: Path,
    persona_name: str,
) -> dict:
    persona_name = (persona_name or "").strip()

    if not persona_name:
        raise ValueError("persona_name is required")

    path = get_radar_path(vault_root, persona_name)

    created = False

    if not path.exists():
        ensure_radar_note(vault_root, persona_name)
        created = True

    content = path.read_text(encoding="utf-8")

    return {
        "persona_name": persona_name,
        "path": path.relative_to(vault_root).as_posix(),
        "created": created,
        "content": content,
    }

def normalise_radar_type(value: str | None) -> str:
    value = (value or "Active").strip()

    if value.lower() not in VALID_RADAR_TYPES:
        return "Active"

    return value.capitalize()


def normalise_pull(value: str | None) -> str:
    value = (value or "medium").strip().lower()

    if value not in VALID_PULL_VALUES:
        return "medium"

    return value


def strip_contribution_headers(text: str) -> str:
    return re.sub(
        r"^\s*##\s+Contribution by .+?\n+",
        "",
        text.strip(),
        flags=re.IGNORECASE,
    )


def format_radar_entry(
    canonical_note_path: str,
    signal_type: str,
    pull: str,
    why_it_is_here: str,
) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    why = strip_contribution_headers(why_it_is_here or "")
    if not why:
        why = "User requested this note remain on Radar."

    return (
        f"{RADAR_START}\n"
        f"Note: [[{canonical_note_path.removesuffix('.md')}]]\n\n"
        f"Type: {normalise_radar_type(signal_type)}\n"
        f"Pull: {normalise_pull(pull)}\n"
        f"Why it is here: {why}\n"
        f"Last Noticed: {today}\n"
        f"{RADAR_END}"
    )


def add_to_radar(
    vault_root: Path,
    persona_name: str,
    note_path: str,
    signal_type: str = "Active",
    pull: str = "medium",
    why_it_is_here: str = "User requested this note remain on Radar.",
) -> dict:
    persona_name = (persona_name or "").strip()
    if not persona_name:
        raise ValueError("persona_name is required")

    if not note_path or not str(note_path).strip():
        raise ValueError("note_path is required")

    radar_path = ensure_radar_note(
        vault_root=vault_root,
        persona_name=persona_name,
    )

    # Reuse existing related-link resolver for canonical vault-relative paths.
    from .activity_stream import resolve_related_link_path

    canonical_path = resolve_related_link_path(vault_root, note_path)

    if not canonical_path:
        raise ValueError(f"Could not resolve note path for Radar entry: {note_path}")

    text = radar_path.read_text(encoding="utf-8")

    entry = format_radar_entry(
        canonical_note_path=canonical_path,
        signal_type=signal_type,
        pull=pull,
        why_it_is_here=why_it_is_here,
    )

    anchor_index = text.find(RADAR_ENTRIES_ANCHOR)
    if anchor_index == -1:
        text = text.rstrip() + "\n\n" + RADAR_ENTRIES_ANCHOR + "\n"
        anchor_index = text.find(RADAR_ENTRIES_ANCHOR)

    insert_at = anchor_index + len(RADAR_ENTRIES_ANCHOR)

    updated = (
        text[:insert_at].rstrip()
        + "\n\n"
        + entry
        + "\n\n"
        + text[insert_at:].lstrip()
    )

    radar_path.write_text(updated.rstrip() + "\n", encoding="utf-8")

    return {
        "persona_name": persona_name,
        "path": radar_path.relative_to(vault_root).as_posix(),
        "note_path": canonical_path,
        "type": normalise_radar_type(signal_type),
        "pull": normalise_pull(pull),
        "updated": True,
    }
