from __future__ import annotations

from typing import Any, Dict, List

from gnw_types import Module, Proposal
from log import setup_logger

logger = setup_logger()


def _clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


class ReflectionModule(Module):
    def __init__(self, learner, emotions, reflection_interval: int = 15) -> None:
        super().__init__("Reflection")
        self.learner = learner
        self.emotions = emotions
        self.reflection_interval = reflection_interval
        self.cycles_since_reflection = 0

    def produce_proposals(self, context: Dict[str, Any]) -> List[Proposal]:
        self.cycles_since_reflection += 1

        total_pain = self.emotions.get_total_pain()
        confusion = self.emotions.state.get("confusion", 0.0)

        should_reflect = (
            total_pain > 70
            or confusion > 0.7
            or self.cycles_since_reflection >= self.reflection_interval
        )

        if not should_reflect:
            return []

        urgency = _clamp((total_pain + confusion * 100.0) / 200.0)
        trigger = "pain" if total_pain > 70 or confusion > 0.7 else "periodic"
        cycle = context.get("cycle")

        logger.info(f"[{self.name}] Proposing reflection (trigger={trigger})")

        return [
            Proposal(
                source=self.name,
                content={"type": "reflect", "payload": {"trigger": trigger, "cycle": cycle}},
                evidence=urgency,
                salience=0.5,
                novelty=0.2,
                urgency=urgency,
            )
        ]

    def on_broadcast(self, content, context):
        if content.type == "reflect":
            self.cycles_since_reflection = 0
