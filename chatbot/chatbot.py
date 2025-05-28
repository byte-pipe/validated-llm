"""Mock ChatBot for testing purposes."""

from typing import Any, List


class ChatBot:
    """Mock ChatBot class."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.messages: List[str] = []

    def chat(self, message: str) -> str:
        """Mock chat method."""
        return "Mock response"
