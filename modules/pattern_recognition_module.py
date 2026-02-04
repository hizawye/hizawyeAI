from __future__ import annotations

from typing import Any, Dict, List

from gnw_types import Module, Proposal
from log import setup_logger

logger = setup_logger()


def _clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


class PatternRecognitionModule(Module):
    def __init__(self, memory, emotions) -> None:
        super().__init__("PatternRecognition")
        self.memory = memory
        self.emotions = emotions
        self.last_pattern_check = 0

    def produce_proposals(self, context: Dict[str, Any]) -> List[Proposal]:
        self.last_pattern_check += 1
        if self.last_pattern_check < 10:
            return []
        self.last_pattern_check = 0

        current_focus = context.get("current_focus")
        if not current_focus or current_focus not in self.memory.graph:
            return []

        working_memory = self.memory.get_working_memory_concepts()
        if len(working_memory) < 2:
            return []

        best_analogy_score = 0.0
        best_pair = None

        for concept in working_memory[:5]:
            if concept == current_focus:
                continue
            score, _ = self.memory.find_analogies(current_focus, concept)
            if score > best_analogy_score:
                best_analogy_score = score
                best_pair = (current_focus, concept)

        if best_analogy_score < 0.3 or not best_pair:
            return []

        curiosity = self.emotions.state.get("curiosity", {}).get("epistemic", 50)
        salience = _clamp(curiosity / 100.0)

        logger.info(
            f"[{self.name}] Proposing analogy exploration: {best_pair} (score={best_analogy_score:.2f})"
        )

        return [
            Proposal(
                source=self.name,
                content={
                    "type": "analogy",
                    "payload": {
                        "concept_pair": best_pair,
                        "analogy_score": best_analogy_score,
                    },
                },
                evidence=_clamp(best_analogy_score),
                salience=salience,
                novelty=_clamp(best_analogy_score),
                urgency=0.4,
            )
        ]
