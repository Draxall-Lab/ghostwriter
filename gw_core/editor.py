# core/editor.py

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import difflib
import hashlib
import json
import time
import uuid
import re


LOCKED_BEGIN = "--LOCKED--"
LOCKED_END = "--/LOCKED--"


@dataclass
class EditPreview:
    preview_id: str
    mutation_class: str
    action: str
    path: str
    target_text: str
    replacement_text: str
    original_hash: str
    proposed_hash: str
    diff: str
    created_at: float
    requires_confirmation: bool
    locked_collision: bool
    ambiguity: bool
    message: str


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalise_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _locked_ranges(text: str) -> list[tuple[int, int]]:
    ranges = []
    start = 0

    while True:
        begin = text.find(LOCKED_BEGIN, start)
        if begin == -1:
            break

        end = text.find(LOCKED_END, begin)
        if end == -1:
            ranges.append((begin, len(text)))
            break

        end += len(LOCKED_END)
        ranges.append((begin, end))
        start = end

    return ranges

def _split_frontmatter(text: str) -> tuple[str, str]:
    text = _normalise_newlines(text)

    if not text.startswith("---\n"):
        return "", text

    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text

    end += len("\n---\n")
    return text[:end], text[end:]

def _overlaps_locked(text: str, start: int, end: int) -> bool:
    for locked_start, locked_end in _locked_ranges(text):
        if start < locked_end and end > locked_start:
            return True
    return False


def _build_diff(original: str, proposed: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            original.splitlines(),
            proposed.splitlines(),
            fromfile="before",
            tofile="after",
            lineterm="",
        )
    )


def preview_block_change(
    note_path: Path,
    target_text: str,
    replacement_text: str,
    *,
    action: str = "rewrite",
    requires_confirmation: bool = True,
) -> EditPreview:
    """
    Creates a dry-run edit proposal.

    No file mutation happens here.
    Commit must later verify that target_text still exists exactly once.

    Hashing is based on the note body, not frontmatter, so governance metadata updates
    do not stale the preview.
    """

    original = _normalise_newlines(note_path.read_text(encoding="utf-8"))
    frontmatter, body = _split_frontmatter(original)

    target_text = _normalise_newlines(target_text)
    replacement_text = _normalise_newlines(replacement_text)

    mutation_class = "substitutive" if action == "rewrite" else "destructive"

    matches = [
        index for index in range(len(body))
        if body.startswith(target_text, index)
    ]

    ambiguity = len(matches) != 1

    if not matches:
        return EditPreview(
            preview_id=str(uuid.uuid4()),
            mutation_class=mutation_class,
            action=action,
            path=str(note_path),
            target_text=target_text,
            replacement_text=replacement_text,
            original_hash=_sha256(body),
            proposed_hash=_sha256(body),
            diff="",
            created_at=time.time(),
            requires_confirmation=requires_confirmation,
            locked_collision=False,
            ambiguity=True,
            message="Target block not found. Refusing preview.",
        )

    if ambiguity:
        return EditPreview(
            preview_id=str(uuid.uuid4()),
            mutation_class=mutation_class,
            action=action,
            path=str(note_path),
            target_text=target_text,
            replacement_text=replacement_text,
            original_hash=_sha256(body),
            proposed_hash=_sha256(body),
            diff="",
            created_at=time.time(),
            requires_confirmation=requires_confirmation,
            locked_collision=False,
            ambiguity=True,
            message="Target block matched multiple locations. Refusing preview.",
        )

    start = matches[0]
    end = start + len(target_text)

    locked_collision = _overlaps_locked(body, start, end)

    if locked_collision:
        return EditPreview(
            preview_id=str(uuid.uuid4()),
            mutation_class=mutation_class,
            action=action,
            path=str(note_path),
            target_text=target_text,
            replacement_text=replacement_text,
            original_hash=_sha256(body),
            proposed_hash=_sha256(body),
            diff="",
            created_at=time.time(),
            requires_confirmation=requires_confirmation,
            locked_collision=True,
            ambiguity=False,
            message="Target overlaps a LOCKED region. Refusing preview.",
        )

    proposed_body = body[:start] + replacement_text + body[end:]

    if action == "remove":
        proposed_body = _cleanup_after_block_removal(proposed_body)

    proposed = frontmatter + proposed_body

    return EditPreview(
        preview_id=str(uuid.uuid4()),
        mutation_class=mutation_class,
        action=action,
        path=str(note_path),
        target_text=target_text,
        replacement_text=replacement_text,
        original_hash=_sha256(body),
        proposed_hash=_sha256(proposed_body),
        diff=_build_diff(original, proposed),
        created_at=time.time(),
        requires_confirmation=requires_confirmation,
        locked_collision=False,
        ambiguity=False,
        message="Preview created. No changes committed.",
    )


def commit_block_change(
    preview: EditPreview | dict,
    *,
    confirmed: bool = False,
) -> tuple[bool, str]:
    """
    Commits a previously generated preview.

    Commit refuses if:
    - confirmation is required but missing
    - note body has changed since preview
    - target no longer matches exactly once
    - target now overlaps LOCKED content
    """

    if isinstance(preview, dict):
        preview = dict(preview)
        preview.pop("governance", None)
        preview = EditPreview(**preview)

    if preview.requires_confirmation and not confirmed:
        return False, "Confirmation required before committing this mutation."

    note_path = Path(preview.path)
    current = _normalise_newlines(note_path.read_text(encoding="utf-8"))

    frontmatter, body = _split_frontmatter(current)

    if _sha256(body) != preview.original_hash:
        return False, (
        "Target note body has changed since preview. Refusing stale commit. "
        f"preview_hash={preview.original_hash} "
        f"current_hash={_sha256(body)} "
        f"preview_target_hash={_sha256(preview.target_text)} "
        f"body_len={len(body)} "
        f"target_matches={body.count(preview.target_text)}"
    )

    matches = [
        index for index in range(len(body))
        if body.startswith(preview.target_text, index)
    ]

    if len(matches) == 0:
        return False, "Target block no longer exists. Refusing commit."

    if len(matches) > 1:
        return False, "Target block is ambiguous. Refusing commit."

    start = matches[0]
    end = start + len(preview.target_text)

    if _overlaps_locked(body, start, end):
        return False, "Target overlaps a LOCKED region. Refusing commit."

    proposed_body = body[:start] + preview.replacement_text + body[end:]

    if preview.action == "remove":
        proposed_body = _cleanup_after_block_removal(proposed_body)

    if _sha256(proposed_body) != preview.proposed_hash:
        return False, (
        "Proposed body hash mismatch. Refusing commit. "
        f"preview_proposed_hash={preview.proposed_hash} "
        f"current_proposed_hash={_sha256(proposed_body)} "
        f"body_len={len(body)} "
        f"proposed_body_len={len(proposed_body)}"
    )

    note_path.write_text(frontmatter + proposed_body, encoding="utf-8")
    return True, "Mutation committed successfully."


def preview_to_json(preview: EditPreview) -> str:
    return json.dumps(asdict(preview), indent=2, ensure_ascii=False)

def preview_block_removal(
    note_path: Path,
    target_text: str,
    *,
    requires_confirmation: bool = True,
) -> EditPreview:
    """
    Creates a dry-run proposal to remove a block.

    No mutation happens here.
    """
    return preview_block_change(
        note_path=note_path,
        target_text=target_text,
        replacement_text="",
        action="remove",
        requires_confirmation=requires_confirmation,
    )

def _cleanup_after_block_removal(text: str) -> str:
    """
    Conservative cleanup after block removal.

    Rules:
    - no leading blank lines at start of file
    - collapse excessive paragraph gaps to one blank line
    - preserve one final newline
    """
    text = re.sub(r"\A\s*\n+", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.rstrip() + "\n"

def commit_block_removal(
    preview: EditPreview | dict,
    *,
    confirmed: bool = False,
) -> tuple[bool, str]:
    """
    Commits a previously previewed block removal.

    Uses the same safety checks as block rewrite.
    """
    return commit_block_change(
        preview=preview,
        confirmed=confirmed,
    )