import time
from typing import Dict

from ..strategies.pinyin_converter import PinyinConverter, digits_to_candidates
from .base_session import BaseSession


class RecognitionSession(BaseSession):
    """Recognition scene session. Keeps full recognition semantics."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pinyin_converter = PinyinConverter()

    def update_display_state(self, result: Dict[str, object]) -> None:
        is_command_result = result.get("engine") == "mediapipe-command"
        hand_count = int(result.get("handCount") or 0)

        if not is_command_result and hand_count >= 2:
            raw_spelling = ""
        else:
            raw_spelling = "" if is_command_result else str(result.get("text") or "").strip()

        if not is_command_result:
            if self._is_in_action_suppression():
                self._vote_buffer.clear()
                self.spelling_buffer = ""
                self.pending_stable_text = ""
                self.pending_stable_started_at = None
                self.last_cached_token = ""
                self._refresh_pinyin_state()
                return

            if hand_count == 0 or not raw_spelling:
                self._vote_buffer.clear()
                self.spelling_buffer = ""
                self.pending_stable_text = ""
                self.pending_stable_started_at = None
                self.last_cached_token = ""
                self._refresh_pinyin_state()
                return

            self._vote_buffer.append(raw_spelling)

        vote_winner = self._compute_vote_winner() if not is_command_result else ""
        self.spelling_buffer = vote_winner

        if not is_command_result:
            self._update_cached_buffer(vote_winner)

        self._refresh_pinyin_state()

        if is_command_result:
            return

        if vote_winner and (not self.process_items or self.process_items[-1] != vote_winner):
            self.process_items.append(vote_winner)

    def display_snapshot(self) -> Dict[str, object]:
        return {
            "processItems": list(self.process_items),
            "spellingBuffer": self.spelling_buffer,
            "cachedBuffer": self.cached_buffer,
            "hanziCandidate": self.hanzi_candidate,
            "hanziCandidates": list(self.hanzi_candidates),
            "candidateIndex": self.candidate_index,
            "stabilityProgress": self.stability_progress(),
            "stabilityDurationMs": int(self.stable_token_duration_seconds * 1000),
        }

    def apply_command_actions(self, command_result: Dict[str, object]) -> Dict[str, object]:
        metadata: Dict[str, object] = {
            "modeChangedByCommand": False,
            "actionPerformed": False,
            "actionType": "",
            "actionToast": "",
        }
        command_gesture = str(command_result.get("commandGesture") or "").strip()
        command_candidate = str(command_result.get("commandCandidate") or "").strip()
        now = time.perf_counter()

        if command_gesture != "CONFIRM" and command_candidate != "CONFIRM":
            self.confirm_ready = True

        if command_gesture != "DELETE" and command_candidate != "DELETE":
            self.delete_ready = True
            self.pending_delete_started_at = None

        if command_gesture != "CLEAR" and command_candidate != "CLEAR":
            self.clear_ready = True
            self.pending_clear_started_at = None

        if command_gesture != "NEXT" and command_candidate != "NEXT":
            self.next_ready = True

        if command_gesture != "SUBMIT" and command_candidate != "SUBMIT":
            self.submit_ready = True

        if command_gesture == "CONFIRM" and self.confirm_ready:
            self.confirm_ready = False
            confirmed_text = self.hanzi_candidate or self.raw_pinyin_buffer
            if confirmed_text:
                self.command_reentry_requires_release = True
                self.reset_display_state(clear_cached=True)
                self.deactivate_command_mode()
                self._start_action_suppression()
                metadata["actionPerformed"] = True
                metadata["actionType"] = "CONFIRM"
                metadata["actionToast"] = confirmed_text
                return metadata

        if command_candidate == "DELETE" and self.delete_ready:
            if self.pending_delete_started_at is None:
                self.pending_delete_started_at = now

            if now - self.pending_delete_started_at >= self.delete_hold_seconds:
                self.delete_ready = False
                self.pending_delete_started_at = None
                self.command_reentry_requires_release = True
                if self.cached_buffer:
                    self.cached_buffer = self.cached_buffer[:-1]
                self.last_cached_token = ""
                self.reset_display_state()
                self.deactivate_command_mode()
                self._start_action_suppression()
                metadata["actionPerformed"] = True
                metadata["actionType"] = "DELETE"
                metadata["actionToast"] = "Deleted"
                return metadata

        if command_candidate == "CLEAR" and self.clear_ready:
            if self.pending_clear_started_at is None:
                self.pending_clear_started_at = now

            if now - self.pending_clear_started_at >= self.clear_hold_seconds:
                self.clear_ready = False
                self.pending_clear_started_at = None
                self.command_reentry_requires_release = True
                self.reset_display_state(clear_cached=True)
                self.deactivate_command_mode()
                self._start_action_suppression()
                metadata["actionPerformed"] = True
                metadata["actionType"] = "CLEAR"
                metadata["actionToast"] = "Cleared"
                return metadata

        if command_gesture == "NEXT" and self.next_ready:
            self.next_ready = False
            if self.hanzi_candidates and len(self.hanzi_candidates) > 1:
                self.candidate_index = (self.candidate_index + 1) % len(self.hanzi_candidates)
                self.hanzi_candidate = self.hanzi_candidates[self.candidate_index]
                metadata["actionPerformed"] = True
                metadata["actionType"] = "NEXT"
                metadata["actionToast"] = self.hanzi_candidate
            return metadata

        if command_gesture == "SUBMIT" and self.submit_ready:
            self.submit_ready = False
            self.command_reentry_requires_release = True
            self.deactivate_command_mode()
            self._start_action_suppression()
            metadata["actionPerformed"] = True
            metadata["actionType"] = "SUBMIT"
            metadata["actionToast"] = ""
            return metadata

        return metadata

    def _refresh_pinyin_state(self) -> None:
        self.raw_pinyin_buffer = self._current_pinyin_buffer()

        if not self.raw_pinyin_buffer:
            self.hanzi_candidate = ""
            self.hanzi_candidates = []
            self.candidate_index = 0
            self._last_pinyin_input = ""
            return

        # 缓存：拼音输入未变化时跳过昂贵的转换计算
        if self.raw_pinyin_buffer == getattr(self, "_last_pinyin_input", ""):
            return
        self._last_pinyin_input = self.raw_pinyin_buffer

        if self.mode == "digits":
            candidates = digits_to_candidates(self.raw_pinyin_buffer)
        else:
            candidates = self.pinyin_converter.convert_with_candidates(self.raw_pinyin_buffer, num=9)

        changed = candidates != self.hanzi_candidates
        if changed:
            self.hanzi_candidates = candidates
            self.candidate_index = 0
        else:
            if self.candidate_index >= len(candidates):
                self.candidate_index = 0

        self.hanzi_candidate = candidates[self.candidate_index] if candidates else ""
