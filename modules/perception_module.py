from __future__ import annotations

from typing import Any, Dict, List

from gnw_types import Module, Proposal
from log import setup_logger

logger = setup_logger()


def _clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


class PerceptionModule(Module):
    def __init__(self, input_stream, memory) -> None:
        super().__init__("Perception")
        self.input_stream = input_stream
        self.memory = memory

    def produce_proposals(self, context: Dict[str, Any]) -> List[Proposal]:
        available = list(self.memory.graph.nodes()) if self.memory.graph.nodes() else None
        event = self.input_stream.next_event(available_concepts=available)
        if not event:
            return []

        concept = event.payload.get("concept")
        novelty = 0.6
        if concept:
            if concept not in self.memory.graph:
                novelty = 1.0
            else:
                node_data = self.memory.graph.nodes[concept]
                novelty = 0.7 if not node_data.get("description") else 0.3

        perception_scale = context.get("perception_scale", 1.0)
        evidence = _clamp(event.salience * perception_scale)
        salience = _clamp(event.salience * perception_scale)
        urgency = _clamp((0.3 + event.salience * 0.5) * perception_scale)

        logger.info(f"[{self.name}] Proposing percept: {event.payload}")

        return [
            Proposal(
                source=self.name,
                content={"type": "percept", "payload": event.payload},
                evidence=evidence,
                salience=salience,
                novelty=novelty,
                urgency=urgency,
            )
        ]
