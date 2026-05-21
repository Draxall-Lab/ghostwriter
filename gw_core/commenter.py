# gw_core/commenter.py

from .block_insert import (
    BlockMatch,
    BlockType,
    Position,
    insert_block_at_anchor,
)


def insert_comment_block(
    note_text: str,
    anchor: str,
    comment_block: str,
    position: Position = "after",
    block_type: BlockType = "any",
) -> tuple[str, BlockMatch]:
    return insert_block_at_anchor(
        note_text=note_text,
        anchor=anchor,
        insert_text=comment_block,
        position=position,
        block_type=block_type,
    )