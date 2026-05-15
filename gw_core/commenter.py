# gw_core/commenter.py

from dataclasses import dataclass
from typing import Literal


BlockType = str
Position = str


@dataclass
class BlockMatch:
    start: int
    end: int
    text: str
    block_type: str


def _split_frontmatter(text: str) -> tuple[str, str]:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            end = text.find("\n", end + 4)
            if end != -1:
                return text[: end + 1], text[end + 1 :]
    return "", text


def _block_type(block: str) -> str:
    stripped = block.lstrip()

    if stripped.startswith("#"):
        return "heading"

    if stripped.startswith(("<!--", "%%")):
        return "marker"

    if stripped.startswith(("- ", "* ", "+ ")):
        return "list_item"

    return "paragraph"


def _iter_blocks(body: str) -> list[BlockMatch]:
    blocks = []
    cursor = 0

    for raw_block in body.split("\n\n"):
        start = cursor
        end = start + len(raw_block)

        if raw_block.strip():
            blocks.append(
                BlockMatch(
                    start=start,
                    end=end,
                    text=raw_block,
                    block_type=_block_type(raw_block),
                )
            )

        cursor = end + 2

    return blocks


def insert_comment_block(
    note_text: str,
    anchor: str,
    comment_block: str,
    position: Position = "after",
    block_type: BlockType = "any",
) -> tuple[str, BlockMatch]:
    frontmatter, body = _split_frontmatter(note_text)

    matches = []
    anchor_l = anchor.lower()

    for block in _iter_blocks(body):
        if block_type != "any" and block.block_type != block_type:
            continue

        if anchor_l in block.text.lower():
            matches.append(block)

    if not matches:
        raise ValueError(f"No matching block found for anchor: {anchor}")

    if len(matches) > 1:
        preview = [
            {
                "block_type": m.block_type,
                "preview": m.text.strip()[:160],
            }
            for m in matches[:5]
        ]
        raise ValueError(f"Anchor matched multiple blocks: {preview}")

    match = matches[0]

    clean_comment = comment_block.strip()
    if not clean_comment:
        raise ValueError("Comment cannot be empty")

    insertion = f"\n\n{clean_comment}\n\n"

    if position == "before":
        new_body = body[: match.start] + clean_comment + "\n\n" + body[match.start :]
    else:
        new_body = body[: match.end] + insertion + body[match.end :].lstrip("\n")

    return frontmatter + new_body, match