from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any, Dict, List, Optional, Callable


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
        novelty_rate: float = 0.0,
        novelty_supplier: Optional[Callable[[], Optional[str]]] = None,
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
        self.novelty_rate = max(0.0, min(1.0, novelty_rate))
        self.novelty_supplier = novelty_supplier
        self.rng = rng or random.Random()
        self._queue: List[InputEvent] = []

    def push_event(self, event: InputEvent) -> None:
        self._queue.append(event)

    def _pick_novel_concept(self) -> Optional[str]:
        if not callable(self.novelty_supplier):
            return None
        try:
            return self.novelty_supplier()
        except Exception:
            return None

    def next_event(self, available_concepts: Optional[List[str]] = None) -> Optional[InputEvent]:
        if self._queue:
            return self._queue.pop(0)

        if self.rng.random() > self.event_rate:
            return None

        concept_pool = available_concepts or self.seed_concepts
        if not concept_pool:
            concept_pool = self.seed_concepts

        if available_concepts and self.novelty_rate > 0.0:
            if self.rng.random() < self.novelty_rate:
                novel = self._pick_novel_concept()
                if novel:
                    salience = self.rng.uniform(0.6, 1.0)
                    return InputEvent(
                        type="concept",
                        payload={"concept": novel},
                        salience=salience,
                    )

        concept = self.rng.choice(concept_pool)
        salience = self.rng.uniform(0.4, 1.0)
        return InputEvent(
            type="concept",
            payload={"concept": concept},
            salience=salience,
        )
