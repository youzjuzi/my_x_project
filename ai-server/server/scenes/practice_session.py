from typing import Dict

from .recognition_session import RecognitionSession


class PracticeSession(RecognitionSession):
    """Practice scene session with lightweight single-token confirmation semantics."""

    def display_snapshot(self) -> Dict[str, object]:
        return {
            "processItems": list(self.process_items),
            "spellingBuffer": self.spelling_buffer,
            "stabilityProgress": self.stability_progress(),
            "stabilityDurationMs": int(self.stable_token_duration_seconds * 1000),
        }

    def _refresh_pinyin_state(self) -> None:
        token = self._current_practice_token()
        self.raw_pinyin_buffer = token.lower()
        self.hanzi_candidate = ""
        self.hanzi_candidates = []
        self.candidate_index = 0

    def apply_command_actions(self, command_result: Dict[str, object]) -> Dict[str, object]:
        metadata: Dict[str, object] = {
            "modeChangedByCommand": False,
            "actionPerformed": False,
            "actionType": "",
            "actionToast": "",
        }
        command_gesture = str(command_result.get("commandGesture") or "").strip()
        command_candidate = str(command_result.get("commandCandidate") or "").strip()

        if command_gesture != "CONFIRM" and command_candidate != "CONFIRM":
            self.confirm_ready = True

        if command_gesture == "CONFIRM" and self.confirm_ready:
            self.confirm_ready = False
            confirmed_text = self._current_practice_token()
            if confirmed_text:
                self.command_reentry_requires_release = True
                self.reset_display_state(clear_cached=True)
                self.deactivate_command_mode()
                self._start_action_suppression()
                metadata["actionPerformed"] = True
                metadata["actionType"] = "CONFIRM"
                metadata["actionToast"] = confirmed_text
                return metadata

        return metadata

    def _current_practice_token(self) -> str:
        if self.spelling_buffer:
            return self.spelling_buffer[-1]
        if self.pending_stable_text:
            return self.pending_stable_text[-1]
        if self.cached_buffer:
            return self.cached_buffer[-1]
        return ""
