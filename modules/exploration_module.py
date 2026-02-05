from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable

from gnw_types import Module, Proposal
from log import setup_logger

logger = setup_logger()


def _clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


class ExplorationModule(Module):
    def __init__(self, memory, emotions, novelty_supplier: Optional[Callable[[], Optional[str]]] = None) -> None:
        super().__init__("Exploration")
        self.memory = memory
        self.emotions = emotions
        self.novelty_supplier = novelty_supplier

    def produce_proposals(self, context: Dict[str, Any]) -> List[Proposal]:
        drives = self.emotions.compute_drive_vector()
        current_focus = context.get("current_focus")
        active_goals = context.get("active_goals", [])

        if not context.get("exploration_allowed", True):
            return []

        if not drives["should_explore"] and active_goals:
            return []

        target = self.memory.find_exploration_target(current_focus, avoid_recent=True)
        if not target and self.novelty_supplier:
            target = self.novelty_supplier()
            if target:
                logger.info(f"[{self.name}] Using novelty target '{target}'")
        if not target:
            return []

        recent_explores = context.get("recent_explores", [])
        if target in recent_explores:
            logger.info(f"[{self.name}] Skipping recent explore target '{target}'")
            return []

        exploration_drive = drives["exploration"]
        boredom = self.emotions.get_total_boredom()

        evidence = _clamp((exploration_drive + boredom) / 200.0)
        salience = _clamp(exploration_drive / 100.0)

        node_data = self.memory.graph.nodes[target] if target in self.memory.graph else {}
        novelty = 0.8 if not node_data.get("description") else 0.4
        urgency = _clamp(boredom / 100.0)

        logger.info(f"[{self.name}] Proposing exploration of '{target}'")

        return [
            Proposal(
                source=self.name,
                content={"type": "explore", "payload": {"target_concept": target}},
                evidence=evidence,
                salience=salience,
                novelty=novelty,
                urgency=urgency,
            )
        ]
