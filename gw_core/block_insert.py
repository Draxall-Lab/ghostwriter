# gw_core/block_insert.py

from dataclasses import dataclass

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
    block_start = 0
    current = []
    current_start = 0
    cursor = 0

    lines = body.splitlines(keepends=True)

    def flush(end_pos: int):
        nonlocal current, current_start
        text = "".join(current).strip("\n")
        if text.strip():
            blocks.append(
                BlockMatch(
                    start=current_start,
                    end=end_pos,
                    text=text,
                    block_type=_block_type(text),
                )
            )
        current = []

    for line in lines:
        line_start = cursor
        line_end = cursor + len(line)
        stripped = line.strip()

        if stripped.startswith("#"):
            if current:
                flush(line_start)

            current = [line]
            current_start = line_start
            flush(line_end)

        elif stripped == "":
            if current:
                flush(line_start)
            current_start = line_end

        else:
            if not current:
                current_start = line_start
            current.append(line)

        cursor = line_end

    if current:
        flush(len(body))

    return blocks


def insert_block_at_anchor(
    note_text: str,
    anchor: str,
    insert_text: str,
    position: Position = "after",
    block_type: BlockType = "any",
) -> tuple[str, BlockMatch]:
    
    if position not in {"before", "after"}:
        raise ValueError("position must be one of: before, after")
    
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

    clean_insert = insert_text.strip()
    if not clean_insert:
        raise ValueError("Insert text cannot be empty")

    if position == "before":
        new_body = body[: match.start] + clean_insert + "\n\n" + body[match.start :]
    else:
        insertion = f"\n\n{clean_insert}\n\n"
        new_body = body[: match.end] + insertion + body[match.end :].lstrip("\n")

    return frontmatter + new_body, match