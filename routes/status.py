import sys
from pathlib import Path

PLUGIN_ROOT = Path.cwd() / "user" / "plugins" / "ghostwriter-for-obsidian"

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from gw_core.vault import vault_status


def handle(path_params=None, body=None, settings=None, **kwargs):
    return vault_status(settings or {})
from gw_core.vault import vault_status