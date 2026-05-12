import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from gw_core.vault import read_note


def handle(path_params=None, body=None, settings=None, **kwargs):
    body = body or {}
    note_path = body.get("path", "")

    return read_note(settings or {}, note_path)