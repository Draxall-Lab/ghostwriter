# gw_core/edit_state.py

from copy import deepcopy
from typing import Any


PENDING_EDIT_PREVIEWS: dict[str, dict[str, Any]] = {}
PENDING_EDIT_CONFIRMATIONS: dict[str, dict[str, Any]] = {}


def store_pending_preview(preview: dict[str, Any]) -> None:
    preview_id = preview.get("preview_id")

    if not isinstance(preview_id, str) or not preview_id:
        raise ValueError("Cannot store preview without preview_id.")

    PENDING_EDIT_PREVIEWS[preview_id] = deepcopy(preview)


def get_pending_preview(preview_id: str) -> dict[str, Any] | None:
    preview = PENDING_EDIT_PREVIEWS.get(preview_id)

    if preview is None:
        return None

    return deepcopy(preview)


def clear_pending_preview(preview_id: str) -> None:
    PENDING_EDIT_PREVIEWS.pop(preview_id, None)
    PENDING_EDIT_CONFIRMATIONS.pop(preview_id, None)


def mark_confirmation_required(preview_id: str) -> None:
    PENDING_EDIT_CONFIRMATIONS[preview_id] = {
        "confirmation_requested": True,
    }


def confirmation_was_requested(preview_id: str) -> bool:
    state = PENDING_EDIT_CONFIRMATIONS.get(preview_id)
    return bool(state and state.get("confirmation_requested"))


def clear_pending_confirmation(preview_id: str) -> None:
    PENDING_EDIT_CONFIRMATIONS.pop(preview_id, None)