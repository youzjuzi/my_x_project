import time
from typing import Dict, Optional

from .recognition_session import RecognitionSession


class PracticeSession(RecognitionSession):
    """Practice scene session with lightweight single-token matching semantics."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._pending_match_token: Optional[str] = None
        self._requires_release = False
        self._last_completed_token = ""

    def update_display_state(self, result: Dict[str, object]) -> None:
        hand_count = int(result.get("handCount") or 0)
        raw_token = str(result.get("text") or "").strip() if hand_count == 1 else ""

        if hand_count == 0 or not raw_token:
            self._clear_practice_tracking(reset_release=True)
            return

        self._vote_buffer.append(raw_token)
        vote_winner = self._compute_vote_winner()
        self.spelling_buffer = vote_winner

        if not vote_winner:
            self.pending_stable_text = ""
            self.pending_stable_started_at = None
            self._refresh_pinyin_state()
            return

        if self._requires_release and vote_winner == self._last_completed_token:
            self.pending_stable_text = ""
            self.pending_stable_started_at = None
            self._refresh_pinyin_state()
            return

        if self._requires_release and vote_winner != self._last_completed_token:
            self._requires_release = False
            self._last_completed_token = ""

        if vote_winner and (not self.process_items or self.process_items[-1] != vote_winner):
            self.process_items.append(vote_winner)

        now = time.perf_counter()
        if vote_winner != self.pending_stable_text:
            self.pending_stable_text = vote_winner
            self.pending_stable_started_at = now
            self._refresh_pinyin_state()
            return

        if self.pending_stable_started_at is None:
            self.pending_stable_started_at = now
            self._refresh_pinyin_state()
            return

        if now - self.pending_stable_started_at < self.stable_token_duration_seconds:
            self._refresh_pinyin_state()
            return

        self._pending_match_token = vote_winner
        self._requires_release = True
        self._last_completed_token = vote_winner
        self.reset_display_state(clear_cached=True)

    def display_snapshot(self) -> Dict[str, object]:
        payload = {
            "processItems": list(self.process_items),
            "spellingBuffer": self.spelling_buffer,
            "stabilityProgress": self.stability_progress(),
            "stabilityDurationMs": int(self.stable_token_duration_seconds * 1000),
        }

        if self._pending_match_token:
            payload.update(
                {
                    "actionPerformed": True,
                    "actionType": "STABLE_MATCH",
                    "actionToast": self._pending_match_token,
                    "practiceMatchedToken": self._pending_match_token,
                }
            )
            self._pending_match_token = None

        return payload

    def _refresh_pinyin_state(self) -> None:
        token = self.spelling_buffer or self.pending_stable_text
        self.raw_pinyin_buffer = token.lower()
        self.hanzi_candidate = ""
        self.hanzi_candidates = []
        self.candidate_index = 0

    def apply_command_actions(self, command_result: Dict[str, object]) -> Dict[str, object]:
        return {
            "modeChangedByCommand": False,
            "actionPerformed": False,
            "actionType": "",
            "actionToast": "",
        }

    def _clear_practice_tracking(self, reset_release: bool = False) -> None:
        self._vote_buffer.clear()
        self.spelling_buffer = ""
        self.pending_stable_text = ""
        self.pending_stable_started_at = None
        self.process_items.clear()
        self._refresh_pinyin_state()
        if reset_release:
            self._requires_release = False
            self._last_completed_token = ""
