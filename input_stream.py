from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any, Dict, List, Optional


@dataclass
class InputEvent:
    type: str
    payload: Dict[str, Any]
    salience: float


class SimulatedInputStream:
    def __init__(
        self,
        event_rate: float = 0.25,
        seed_concepts: Optional[List[str]] = None,
        rng: Optional[random.Random] = None,
    ) -> None:
        self.event_rate = event_rate
        self.seed_concepts = seed_concepts or [
            "knowledge",
            "curiosity",
            "memory",
            "emotion",
            "goal",
            "creativity",
            "analysis",
        ]
        self.rng = rng or random.Random()
        self._queue: List[InputEvent] = []

    def push_event(self, event: InputEvent) -> None:
        self._queue.append(event)

    def next_event(self, available_concepts: Optional[List[str]] = None) -> Optional[InputEvent]:
        if self._queue:
            return self._queue.pop(0)

        if self.rng.random() > self.event_rate:
            return None

        concept_pool = available_concepts or self.seed_concepts
        if not concept_pool:
            concept_pool = self.seed_concepts

        concept = self.rng.choice(concept_pool)
        salience = self.rng.uniform(0.4, 1.0)
        return InputEvent(
            type="concept",
            payload={"concept": concept},
            salience=salience,
        )
