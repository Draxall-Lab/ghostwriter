# gw_core/activity_stream.py

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)

STREAM_REL_PATH = Path("_ghostwriter/activity-stream.md")
ENTRY_START = "--STREAM-ENTRY--"
ENTRY_END = "--/STREAM-ENTRY--"

DEFAULT_MAX_ENTRIES = 250

VALID_ACTIVITY_TYPES = {
    "read",
    "write",
    "append",
    "comment",
    "insert",
    "frontmatter",
    "denied",
    "breadcrumb",
}

WIKILINK_RE = re.compile(
    r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]"
)


def extract_frontmatter_related_links(text: str) -> list[str]:
    if not text.startswith("---"):
        return []

    end = text.find("\n---", 3)
    if end == -1:
        return []

    frontmatter = text[3:end]
    links: list[str] = []
    in_related = False

    for line in frontmatter.splitlines():
        stripped = line.strip()

        if stripped.lower().startswith("related:"):
            _, value = stripped.split(":", 1)
            value = value.strip().strip('"').strip("'")

            if value:
                wikilinks = extract_body_wikilinks(value)
                if wikilinks:
                    links.extend(wikilinks)
                else:
                    links.append(value)

                in_related = False
            else:
                in_related = True

            continue

        if in_related:
            if ":" in stripped and not stripped.startswith("- "):
                break

            if stripped.startswith("- "):
                raw = stripped[2:].strip().strip('"').strip("'")
                wikilinks = extract_body_wikilinks(raw)

                if wikilinks:
                    links.extend(wikilinks)
                elif raw:
                    links.append(raw)

    return links


def extract_body_wikilinks(text: str) -> list[str]:
    return [
        match.group(1).strip()
        for match in WIKILINK_RE.finditer(text)
    ]

def check_stream(
    vault_root: Path,
    persona_name: str | None = None,
    max_entries: int = 10,
) -> list[dict]:
    stream_path = ensure_activity_stream(vault_root)
    text = stream_path.read_text(encoding="utf-8")

    entries = parse_stream_entries(text)

    if persona_name and persona_name.strip():
        wanted = persona_name.strip().lower()
        entries = [
            entry for entry in entries
            if entry.get("persona", "").strip().lower() == wanted
        ]

    return entries[:max_entries]

def parse_stream_entries(text: str) -> list[dict]:
    pattern = re.compile(
        rf"{re.escape(ENTRY_START)}(.*?){re.escape(ENTRY_END)}",
        re.DOTALL,
    )

    entries: list[dict] = []

    for match in pattern.finditer(text):
        body = match.group(1).strip()
        entries.append(parse_stream_entry_body(body))

    return entries


def parse_stream_entry_body(body: str) -> dict:
    entry: dict = {
        "date": "",
        "persona": "",
        "type": "",
        "path": "",
        "related": [],
    }

    current_field = None

    for raw_line in body.splitlines():
        line = raw_line.rstrip()

        if not line.strip():
            continue

        if line.startswith("- ") and current_field == "related":
            entry["related"].append(line[2:].strip())
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key_norm = key.strip().lower()
        value = value.strip()

        if key_norm == "date":
            entry["date"] = value
            current_field = "date"
        elif key_norm == "persona":
            entry["persona"] = value
            current_field = "persona"
        elif key_norm == "type":
            entry["type"] = value
            current_field = "type"
        elif key_norm == "path":
            entry["path"] = value
            current_field = "path"
        elif key_norm == "related":
            current_field = "related"

    return entry

def ensure_activity_stream(vault_root: Path) -> Path:
    stream_path = vault_root / STREAM_REL_PATH
    stream_path.parent.mkdir(parents=True, exist_ok=True)

    if not stream_path.exists():
        stream_path.write_text(
            "---\n"
            "type:\n"
            "  - system\n"
            "  - activity-stream\n"
            "created by: Ghostwriter\n"
            "---\n\n",
            encoding="utf-8",
        )

    return stream_path

def strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text

    end = text.find("\n---", 3)
    if end == -1:
        return text

    return text[end + 4:]

def extract_related_links_for_note(
    vault_root: Path,
    note_path: str,
) -> list[str]:
    target = vault_root / note_path

    if not target.exists() or not target.is_file():
        return []

    text = target.read_text(encoding="utf-8")

    related = []
    related.extend(extract_frontmatter_related_links(text))
    related.extend(extract_body_wikilinks(strip_frontmatter(text)))

    return dedupe_preserve_order(
        resolve_related_link_path(vault_root, item)
        for item in related
        if item
    )

def resolve_related_link_path(vault_root: Path, link: str) -> str:
    raw = normalise_stream_path(link)

    if not raw:
        return ""

    exact = vault_root / raw
    if exact.exists() and exact.is_file() and exact.suffix == ".md":
        return exact.relative_to(vault_root).as_posix()

    if not raw.endswith(".md"):
        exact_md = vault_root / f"{raw}.md"
        if exact_md.exists() and exact_md.is_file():
            return exact_md.relative_to(vault_root).as_posix()

    wanted_filename = raw if raw.endswith(".md") else f"{raw}.md"
    wanted_title = raw.removesuffix(".md").lower()

    matches: list[Path] = []

    for path in vault_root.rglob("*.md"):
        rel = path.relative_to(vault_root).as_posix()

        if rel.startswith("_ghostwriter/"):
            continue

        if path.name.lower() == wanted_filename.lower() or path.stem.lower() == wanted_title:
            matches.append(path)

    if len(matches) == 1:
        return matches[0].relative_to(vault_root).as_posix()

    # If missing or ambiguous, preserve the original link text.
    return raw

def record_activity(
    vault_root: Path,
    persona_name: str,
    activity_type: str,
    note_path: str,
    related: list[str] | None = None,
    max_entries: int = DEFAULT_MAX_ENTRIES,
) -> None:
    """
    Record a successful Ghostwriter activity event.

    This must never block the parent tool action. If logging fails, warn and continue.
    """
    try:
        if not persona_name or not persona_name.strip():
            return

        activity_type = (activity_type or "").strip().lower()
        if activity_type not in VALID_ACTIVITY_TYPES:
            logger.warning("[Ghostwriter] Unknown activity type: %s", activity_type)
            return

        note_path = normalise_stream_path(note_path)
        if not note_path:
            return

        stream_path = ensure_activity_stream(vault_root)

        auto_related = extract_related_links_for_note(
            vault_root=vault_root,
            note_path=note_path,
        )

        combined_related = dedupe_preserve_order([
            *(related or []),
            *auto_related,
        ])

        entry = format_stream_entry(
            persona_name=persona_name.strip(),
            activity_type=activity_type,
            note_path=note_path,
            related=combined_related,
        )

        existing = stream_path.read_text(encoding="utf-8")

        existing = maintain_activity_stream(
            existing,
            max_entries=max_entries,
        )

        updated = insert_entry_newest_first(existing, entry)

        stream_path.write_text(updated, encoding="utf-8")

    except Exception as exc:
        logger.warning("[Ghostwriter] Activity stream logging failed: %s", exc)

def maintain_activity_stream(
    text: str,
    max_entries: int = DEFAULT_MAX_ENTRIES,
) -> str:
    text = prune_stream_entries(text, max_entries=max_entries)

    return text.rstrip() + "\n"

def display_stream_path(path: str | Path) -> str:
    raw = normalise_stream_path(path)
    return f"/{raw}" if raw else ""

def format_stream_entry(
    persona_name: str,
    activity_type: str,
    note_path: str,
    related: list[str],
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        ENTRY_START,
        f"Date: {now}",
        f"Persona: {persona_name}",
        f"Type: {activity_type}",
        f"Path: `{display_stream_path(note_path)}`",
    ]

    clean_related = dedupe_preserve_order(
        normalise_stream_path(item)
        for item in related
        if item and normalise_stream_path(item) != note_path
    )

    if clean_related:
        lines.append("Related:")
        for item in clean_related:
            lines.append(f"- `{display_stream_path(item)}`")

    lines.append(ENTRY_END)

    return "\n" + "\n".join(lines) + "\n\n"


def insert_entry_newest_first(existing: str, entry: str) -> str:
    text = existing.rstrip() + "\n\n" if existing.strip() else ""

    first_entry = text.find(ENTRY_START)
    if first_entry != -1:
        return text[:first_entry].rstrip() + "\n" + entry + text[first_entry:].lstrip()

    return text + entry


def prune_stream_entries(text: str, max_entries: int = DEFAULT_MAX_ENTRIES) -> str:
    if max_entries <= 0:
        return text

    pattern = re.compile(
        rf"\n?{re.escape(ENTRY_START)}.*?{re.escape(ENTRY_END)}\s*",
        re.DOTALL,
    )

    matches = list(pattern.finditer(text))
    if len(matches) <= max_entries:
        return text

    cutoff = matches[max_entries - 1].end()
    return text[:cutoff].rstrip() + "\n"


def normalise_stream_path(path: str | Path) -> str:
    raw = str(path).strip().replace("\\", "/")

    while raw.startswith("./"):
        raw = raw[2:]

    return raw.lstrip("/")


def dedupe_preserve_order(items) -> list[str]:
    seen = set()
    result = []

    for item in items:
        if not item:
            continue
        if item in seen:
            continue

        seen.add(item)
        result.append(item)

    return result