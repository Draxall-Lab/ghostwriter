import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from gw_core.vault import list_markdown_notes


def handle(path_params=None, body=None, settings=None, **kwargs):
    body = body or {}
    include_meta = bool(body.get("include_meta", False))

    return list_markdown_notes(settings or {}, include_meta=include_meta)