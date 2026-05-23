# routes/check_stream.py or wherever your Ghostwriter tool handlers live

from pathlib import Path
from gw_core.activity_stream import check_stream


def ghostwriter_check_stream(
    vault_root: Path,
    persona_name: str | None = None,
    max_entries: int = 10,
) -> dict:
    entries = check_stream(
        vault_root=vault_root,
        persona_name=persona_name,
        max_entries=max_entries,
    )

    return {
        "ok": True,
        "count": len(entries),
        "persona_filter": persona_name or "all",
        "entries": entries,
    }