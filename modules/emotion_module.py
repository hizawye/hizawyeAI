from __future__ import annotations

from typing import Any, Dict

from gnw_types import Module
from log import setup_logger

logger = setup_logger()


class EmotionModule(Module):
    def __init__(self, emotions) -> None:
        super().__init__("Emotion")
        self.emotions = emotions

    def produce_proposals(self, context: Dict[str, Any]):
        return []

    def on_broadcast(self, content, context: Dict[str, Any]) -> None:
        if content.type == "percept":
            self.emotions.update_on_exploration()
            logger.info(f"[{self.name}] Percept updated emotions")
        elif content.type == "reflect":
            self.emotions.state["confusion"] = max(0, self.emotions.state["confusion"] - 0.1)
            logger.info(f"[{self.name}] Reflection reduced confusion")
