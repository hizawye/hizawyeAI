from __future__ import annotations

import json
import random
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple

from gnw_types import Proposal, WorkspaceContent, WorkspaceState, Module
from log import setup_logger

logger = setup_logger()


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


class Workspace:
    def __init__(
        self,
        modules: List[Module],
        ignition_threshold: float = 0.75,
        persistence_threshold: float = 0.4,
        decay_rate: float = 0.9,
        ignited_decay_rate: float = 0.95,
        noise: float = 0.03,
        weights: Optional[Dict[str, float]] = None,
        history_limit: int = 50,
    ) -> None:
        self.modules = modules
        self.ignition_threshold = ignition_threshold
        self.persistence_threshold = persistence_threshold
        self.decay_rate = decay_rate
        self.ignited_decay_rate = ignited_decay_rate
        self.noise = noise
        self.weights = weights or {
            "evidence": 0.4,
            "salience": 0.25,
            "novelty": 0.2,
            "urgency": 0.15,
        }
        self.history_limit = history_limit

        self.context: Dict[str, Any] = {}
        self.state = WorkspaceState()
        self.last_proposals: List[Proposal] = []
        self.last_winner_proposal: Optional[Proposal] = None

    def update_context(self, **kwargs: Any) -> None:
        self.context.update(kwargs)

    def cycle(self) -> Optional[WorkspaceContent]:
        logger.info("=== GNW Workspace Cycle Start ===")

        for module in self.modules:
            module.tick(self.context)

        proposals = self._collect_proposals()
        aggregated = self._aggregate_proposals(proposals)
        scored = self._score_proposals(aggregated)
        self.last_proposals = scored

        if scored:
            winner = max(scored, key=lambda p: p.score or 0.0)
            if (winner.score or 0.0) >= self.ignition_threshold:
                self.last_winner_proposal = winner
                content = self._ignite(winner)
                self._broadcast(content)
                return content
            self.last_winner_proposal = None

        persisted = self._decay_and_persist()
        if persisted:
            self._broadcast(persisted)
            return persisted

        logger.info("No ignition and no persistent content.")
        self.last_winner_proposal = None
        return None

    def _collect_proposals(self) -> List[Proposal]:
        proposals: List[Proposal] = []
        for module in self.modules:
            module_proposals = module.produce_proposals(self.context)
            if module_proposals:
                proposals.extend(module_proposals)
        return proposals

    def _aggregate_proposals(self, proposals: Iterable[Proposal]) -> List[Proposal]:
        buckets: Dict[Tuple[str, str], List[Proposal]] = {}
        for proposal in proposals:
            key = self._content_key(proposal.content)
            buckets.setdefault(key, []).append(proposal)

        aggregated: List[Proposal] = []
        for (content_type, payload_key), grouped in buckets.items():
            evidence_sum = sum(p.evidence for p in grouped)
            evidence = _clamp(evidence_sum, 0.0, 1.0)
            salience = sum(p.salience for p in grouped) / len(grouped)
            novelty = sum(p.novelty for p in grouped) / len(grouped)
            urgency = sum(p.urgency for p in grouped) / len(grouped)
            sources = [p.source for p in grouped]
            content = grouped[0].content
            aggregated.append(
                Proposal(
                    source=sources[0] if len(sources) == 1 else "multi",
                    content=content,
                    evidence=evidence,
                    salience=salience,
                    novelty=novelty,
                    urgency=urgency,
                    sources=sources,
                )
            )
        return aggregated

    def _score_proposals(self, proposals: List[Proposal]) -> List[Proposal]:
        attention_gain = _clamp(self.context.get("attention_gain", 1.0), 0.5, 1.5)
        current_focus = self.context.get("current_focus")

        for proposal in proposals:
            base_score = (
                self.weights["evidence"] * proposal.evidence
                + self.weights["salience"] * proposal.salience
                + self.weights["novelty"] * proposal.novelty
                + self.weights["urgency"] * proposal.urgency
            )

            focus_bonus = 0.0
            if current_focus and self._content_mentions_focus(proposal.content, current_focus):
                focus_bonus = 0.1

            repetition_penalty = 0.0
            if self._content_repeats(proposal.content, self.context.get("recent_actions", [])):
                repetition_penalty = 0.1

            noise = random.uniform(-self.noise, self.noise)
            proposal.score = _clamp(
                (base_score + focus_bonus - repetition_penalty + noise) * attention_gain,
                0.0,
                1.5
            )

            logger.info(
                f"  [{proposal.source}] {proposal.content.get('type')} score={proposal.score:.3f}"
            )

        return proposals

    def _ignite(self, proposal: Proposal) -> WorkspaceContent:
        now = time.time()
        content = WorkspaceContent(
            type=proposal.content["type"],
            payload=proposal.content.get("payload", {}),
            activation=_clamp(proposal.score or 0.0, 0.0, 1.5),
            ignited=True,
            timestamp=now,
            sources=proposal.sources,
        )
        self.state.current = content
        self.state.history.append(content)
        if len(self.state.history) > self.history_limit:
            self.state.history = self.state.history[-self.history_limit :]

        logger.info(
            f">>> IGNITION: {content.type} activation={content.activation:.3f} sources={content.sources}"
        )
        return content

    def _decay_and_persist(self) -> Optional[WorkspaceContent]:
        if not self.state.current:
            return None

        decay_rate = self.ignited_decay_rate if self.state.current.ignited else self.decay_rate
        self.state.current.activation *= decay_rate
        if self.state.current.activation < self.persistence_threshold:
            logger.info("Workspace content decayed below persistence threshold.")
            self.state.current = None
            return None

        self.state.current.ignited = False
        logger.info(
            f"Workspace persistence: {self.state.current.type} activation={self.state.current.activation:.3f}"
        )
        return self.state.current

    def _broadcast(self, content: WorkspaceContent) -> None:
        for module in self.modules:
            module.on_broadcast(content, self.context)

    def _content_key(self, content: Dict[str, Any]) -> Tuple[str, str]:
        payload = content.get("payload", {})
        payload_key = json.dumps(payload, sort_keys=True)
        return content.get("type", "unknown"), payload_key

    def _content_mentions_focus(self, content: Dict[str, Any], focus: str) -> bool:
        payload = content.get("payload", {})
        for key in ("concept", "target_concept"):
            if payload.get(key) == focus:
                return True
        return False

    def _content_repeats(self, content: Dict[str, Any], recent_actions: List[Dict[str, Any]]) -> bool:
        if not recent_actions:
            return False
        content_type = content.get("type")
        payload = content.get("payload", {})
        concept = payload.get("concept") or payload.get("target_concept")
        for action in recent_actions[-3:]:
            if action.get("type") == content_type and action.get("concept") == concept:
                return True
        return False
