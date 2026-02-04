from __future__ import annotations

from typing import Any, Dict, List

from gnw_types import Module, Proposal
from log import setup_logger

logger = setup_logger()


def _clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


class GoalPlannerModule(Module):
    def __init__(self, planner, emotions) -> None:
        super().__init__("GoalPlanner")
        self.planner = planner
        self.emotions = emotions

    def produce_proposals(self, context: Dict[str, Any]) -> List[Proposal]:
        active_goals = context.get("active_goals", [])
        if not active_goals:
            return []

        current_goal = active_goals[0]

        if self.planner.should_retreat(current_goal):
            alternative = self.planner.generate_alternative_goal(current_goal)
            logger.info(
                f"[{self.name}] Proposing strategy switch for '{current_goal['concept']}'"
            )
            return [
                Proposal(
                    source=self.name,
                    content={
                        "type": "goal_switch",
                        "payload": {
                            "old_goal": current_goal,
                            "new_goal": alternative,
                            "concept": current_goal["concept"],
                        },
                    },
                    evidence=0.7,
                    salience=0.5,
                    novelty=0.3,
                    urgency=0.6,
                )
            ]

        drives = self.emotions.compute_drive_vector()
        confidence = self.emotions.state.get("confidence", 0.5)
        focus_drive = drives["focus"] / 100.0

        evidence = _clamp(focus_drive * confidence)
        salience = _clamp(focus_drive)
        novelty = 0.2
        urgency = _clamp(confidence)

        logger.info(
            f"[{self.name}] Proposing goal execution: '{current_goal['concept']}'"
        )

        return [
            Proposal(
                source=self.name,
                content={
                    "type": "goal_execute",
                    "payload": {"goal": current_goal, "concept": current_goal["concept"]},
                },
                evidence=evidence,
                salience=salience,
                novelty=novelty,
                urgency=urgency,
            )
        ]
