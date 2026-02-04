from __future__ import annotations

from typing import Any, Dict, Optional

from gnw_types import Module
from log import setup_logger

logger = setup_logger()


class MemoryModule(Module):
    def __init__(self, memory) -> None:
        super().__init__("Memory")
        self.memory = memory

    def produce_proposals(self, context: Dict[str, Any]):
        return []

    def on_broadcast(self, content, context: Dict[str, Any]) -> None:
        concept = self._extract_concept(content)
        if not concept:
            return

        if not self.memory.graph.has_node(concept):
            self.memory.add_node(concept)

        self.memory.update_working_memory(concept)
        logger.info(f"[{self.name}] Broadcast updated working memory: {concept}")

    def _extract_concept(self, content) -> Optional[str]:
        payload = content.payload or {}
        return payload.get("concept") or payload.get("target_concept")
