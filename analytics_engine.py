"""
Analytics Engine for Hizawye AI
Captures real-time data during AI runtime for analysis and reporting.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class AnalyticsEngine:
    """Collects runtime analytics data for Hizawye AI sessions."""

    def __init__(self, mind_directory: str = "hizawye_mind"):
        self.mind_dir = Path(mind_directory)
        self.analytics_dir = self.mind_dir / "analytics"
        self.analytics_dir.mkdir(parents=True, exist_ok=True)

        self.session_data: Dict[str, Any] = {}
        self.session_id: Optional[str] = None
        self.start_time: Optional[float] = None
        self._persistence_key: Optional[str] = None
        self._persistence_type: Optional[str] = None
        self._persistence_run: int = 0

    def start_session(self) -> str:
        """Initialize a new analytics session."""
        self.session_id = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.start_time = time.time()

        self.session_data = {
            "session_id": self.session_id,
            "start_time": self.session_id,
            "cycles": 0,
            "runtime_seconds": 0.0,
            "workspace_competition": {},
            "workspace_events": {
                "ignitions": 0,
                "persisted": 0,
                "none": 0,
                "by_type": {},
                "activation": {
                    "ignition_sum": 0.0,
                    "ignition_count": 0,
                    "persist_sum": 0.0,
                    "persist_count": 0
                },
                "persistence_runs": []
            },
            "emotional_timeline": [],
            "concepts_learned": {},
            "memory_growth": {
                "initial_nodes": 0,
                "final_nodes": 0,
                "nodes_added": 0,
                "connections_added": 0
            },
            "strategies_used": {},
            "pain_events": [],
            "reflections": []
        }

        self._persistence_key = None
        self._persistence_type = None
        self._persistence_run = 0

        return self.session_id

    def record_emotional_state(self, cycle: int, emotions: Dict[str, float]):
        """Record emotional state at a specific cycle."""
        emotional_snapshot = {
            "cycle": cycle,
            **emotions
        }
        self.session_data["emotional_timeline"].append(emotional_snapshot)

        # Handle nested pain dicts from EmotionalSystem
        pain = emotions.get("pain", 0)
        if isinstance(pain, dict):
            total_pain = sum(pain.values()) / max(len(pain), 1)
            frustration = pain.get("frustration", 0)
        else:
            total_pain = pain
            frustration = emotions.get("frustration", 0)

        # Track pain events
        if total_pain > 50:
            self.session_data["pain_events"].append({
                "cycle": cycle,
                "pain": total_pain,
                "frustration": frustration,
                "confusion": emotions.get("confusion", 0)
            })

    def record_proposal_competition(
        self,
        cycle: int,
        proposals: List[Any],
        winner: Any
    ):
        """Track which threads compete and which wins."""
        winner_sources = set()
        if winner is not None:
            if hasattr(winner, "sources") and isinstance(winner.sources, list):
                winner_sources = set(winner.sources)
            else:
                winner_sources = {getattr(winner, "source", "unknown")}

        for proposal in proposals:
            sources = []
            if hasattr(proposal, "sources") and isinstance(proposal.sources, list):
                sources = proposal.sources
            else:
                sources = [
                    getattr(proposal, "thread_type", None)
                    or getattr(proposal, "source", "unknown")
                ]

            for thread_name in sources:
                if thread_name not in self.session_data["workspace_competition"]:
                    self.session_data["workspace_competition"][thread_name] = {
                        "wins": 0,
                        "total_proposals": 0
                    }

                self.session_data["workspace_competition"][thread_name]["total_proposals"] += 1

                if thread_name in winner_sources:
                    self.session_data["workspace_competition"][thread_name]["wins"] += 1

    def record_concept_learned(
        self,
        concept: str,
        strategy: str,
        success: bool,
        pain_cost: float,
        attempts: int = 1
    ):
        """Track concept learning events."""
        if concept not in self.session_data["concepts_learned"]:
            self.session_data["concepts_learned"][concept] = {
                "attempts": 0,
                "strategies_tried": [],
                "success": False,
                "total_pain": 0.0,
                "successful_strategy": None
            }

        concept_data = self.session_data["concepts_learned"][concept]
        concept_data["attempts"] += attempts
        concept_data["total_pain"] += pain_cost

        if strategy not in concept_data["strategies_tried"]:
            concept_data["strategies_tried"].append(strategy)

        if success:
            concept_data["success"] = True
            concept_data["successful_strategy"] = strategy

        # Track strategy performance
        if strategy not in self.session_data["strategies_used"]:
            self.session_data["strategies_used"][strategy] = {
                "attempts": 0,
                "successes": 0,
                "total_pain": 0.0
            }

        strategy_data = self.session_data["strategies_used"][strategy]
        strategy_data["attempts"] += attempts
        strategy_data["total_pain"] += pain_cost
        if success:
            strategy_data["successes"] += 1

    def record_memory_growth(
        self,
        nodes_added: int = 0,
        edges_added: int = 0,
        total_nodes: int = 0
    ):
        """Track memory graph growth."""
        if self.session_data["memory_growth"]["initial_nodes"] == 0:
            self.session_data["memory_growth"]["initial_nodes"] = total_nodes

        self.session_data["memory_growth"]["nodes_added"] += nodes_added
        self.session_data["memory_growth"]["connections_added"] += edges_added
        self.session_data["memory_growth"]["final_nodes"] = total_nodes

    def record_reflection(self, cycle: int, trigger: str, insights: List[str]):
        """Track meta-cognitive reflection events."""
        self.session_data["reflections"].append({
            "cycle": cycle,
            "trigger": trigger,
            "insights": insights
        })

    def record_workspace_event(self, cycle: int, content: Optional[Any]):
        """Track ignition, persistence, and activation metrics."""
        events = self.session_data["workspace_events"]

        if content is None:
            events["none"] += 1
            self._flush_persistence_run()
            return

        content_type = getattr(content, "type", "unknown")
        by_type = events["by_type"].setdefault(content_type, {"ignitions": 0, "persisted": 0})

        activation = float(getattr(content, "activation", 0.0) or 0.0)
        if getattr(content, "ignited", False):
            events["ignitions"] += 1
            by_type["ignitions"] += 1
            events["activation"]["ignition_sum"] += activation
            events["activation"]["ignition_count"] += 1
            self._flush_persistence_run()
        else:
            events["persisted"] += 1
            by_type["persisted"] += 1
            events["activation"]["persist_sum"] += activation
            events["activation"]["persist_count"] += 1

            key = self._content_key(content_type, getattr(content, "payload", {}))
            if self._persistence_key == key:
                self._persistence_run += 1
            else:
                self._flush_persistence_run()
                self._persistence_key = key
                self._persistence_type = content_type
                self._persistence_run = 1

    def increment_cycle(self):
        """Increment the cycle counter."""
        self.session_data["cycles"] += 1

    def end_session(self):
        """Finalize session data."""
        if self.start_time:
            self.session_data["runtime_seconds"] = time.time() - self.start_time
            self.session_data["end_time"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self._flush_persistence_run()

    def _content_key(self, content_type: str, payload: Dict[str, Any]) -> str:
        try:
            payload_key = json.dumps(payload, sort_keys=True)
        except (TypeError, ValueError):
            payload_key = str(payload)
        return f"{content_type}:{payload_key}"

    def _flush_persistence_run(self):
        if self._persistence_run > 0:
            self.session_data["workspace_events"]["persistence_runs"].append({
                "content_type": self._persistence_type or "unknown",
                "length": self._persistence_run
            })
        self._persistence_key = None
        self._persistence_type = None
        self._persistence_run = 0

    def save(self) -> Path:
        """Save analytics data to JSON file."""
        if not self.session_id:
            raise ValueError("No active session to save")

        filename = f"session_{self.session_id.replace(':', '-')}.json"
        filepath = self.analytics_dir / filename

        with open(filepath, 'w') as f:
            json.dump(self.session_data, f, indent=2)

        # Also save as "latest" for quick access
        latest_path = self.analytics_dir / "session_latest.json"
        with open(latest_path, 'w') as f:
            json.dump(self.session_data, f, indent=2)

        return filepath

    @staticmethod
    def load_session(filepath: Path) -> Dict[str, Any]:
        """Load analytics data from a session file."""
        with open(filepath, 'r') as f:
            return json.load(f)

    def get_summary_stats(self) -> Dict[str, Any]:
        """Generate quick summary statistics."""
        total_concepts = len(self.session_data["concepts_learned"])
        successful_concepts = sum(
            1 for c in self.session_data["concepts_learned"].values()
            if c["success"]
        )
        workspace_events = self.session_data.get("workspace_events", {})
        ignitions = workspace_events.get("ignitions", 0)
        persisted = workspace_events.get("persisted", 0)
        none_events = workspace_events.get("none", 0)

        return {
            "session_id": self.session_id,
            "cycles": self.session_data["cycles"],
            "runtime_seconds": self.session_data.get("runtime_seconds", 0),
            "total_concepts": total_concepts,
            "successful_concepts": successful_concepts,
            "success_rate": successful_concepts / total_concepts if total_concepts > 0 else 0,
            "strategies_used": len(self.session_data["strategies_used"]),
            "pain_events": len(self.session_data["pain_events"]),
            "reflections": len(self.session_data["reflections"]),
            "ignitions": ignitions,
            "persisted": persisted,
            "no_content": none_events
        }
