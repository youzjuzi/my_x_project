from .practice_session import PracticeSession


class ChallengeSession(PracticeSession):
    """Challenge scene session with single-hit stable matching for letters and digits."""

    def supported_modes(self) -> tuple[str, ...]:
        return ("digits", "letters")

    def allows_detector_command_mode(self) -> bool:
        return False
