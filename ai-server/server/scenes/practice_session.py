import time
from typing import Dict, Optional

from .recognition_session import RecognitionSession


class PracticeSession(RecognitionSession):
    """Practice scene session with isolated per-mode matching semantics."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._pending_match_token: Optional[str] = None
        self._requires_release = False
        self._last_completed_token = ""
        self._command_practice_progress = 0.0

    def supported_modes(self) -> tuple[str, ...]:
        return ("digits", "letters", "commands")

    def allows_detector_command_mode(self) -> bool:
        return False

    def update_display_state(self, result: Dict[str, object]) -> None:
        if self.mode == "commands":
            self._update_command_practice_state(result)
            return

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
            "stabilityProgress": self._command_practice_progress if self.mode == "commands" else self.stability_progress(),
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

    def _update_command_practice_state(self, result: Dict[str, object]) -> None:
        hand_count = int(result.get("commandHandCount") or result.get("handCount") or 0)
        command_candidate = str(result.get("commandCandidate") or "").strip()
        command_gesture = str(result.get("commandGesture") or "").strip()
        display_token = command_gesture or command_candidate
        self._command_practice_progress = float(result.get("commandCandidateProgress") or 0.0)

        if hand_count < 2 or not display_token:
            self._clear_practice_tracking(reset_release=True)
            return

        self.spelling_buffer = display_token
        self.pending_stable_text = display_token
        self.pending_stable_started_at = None
        self.process_items.clear()
        self.process_items.append(display_token)
        self._refresh_pinyin_state()

        if self._requires_release:
            return

        if command_gesture:
            self._pending_match_token = command_gesture
            self._requires_release = True
            self._last_completed_token = command_gesture
            self._command_practice_progress = 0.0

    def _clear_practice_tracking(self, reset_release: bool = False) -> None:
        self._vote_buffer.clear()
        self.spelling_buffer = ""
        self.pending_stable_text = ""
        self.pending_stable_started_at = None
        self.process_items.clear()
        self._pending_match_token = None
        self._command_practice_progress = 0.0
        self._refresh_pinyin_state()
        if reset_release:
            self._requires_release = False
            self._last_completed_token = ""
