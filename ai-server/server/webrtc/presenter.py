from typing import Dict

from ..scenes import BaseSession


def build_result_payload(session: BaseSession, result: Dict[str, object]) -> Dict[str, object]:
    if result.get("resetDisplayState"):
        session.reset_display_state()
    if not result.get("suppressDisplayStateUpdate"):
        session.update_display_state(result)
    payload = dict(result)
    payload.update(session.display_snapshot())
    return payload
