from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Proposal:
    source: str
    content: Dict[str, Any]
    evidence: float
    salience: float
    novelty: float
    urgency: float
    sources: List[str] = field(default_factory=list)
    score: Optional[float] = None

    def __post_init__(self) -> None:
        if not self.sources:
            self.sources = [self.source]


@dataclass
class WorkspaceContent:
    type: str
    payload: Dict[str, Any]
    activation: float
    ignited: bool
    timestamp: float
    sources: List[str] = field(default_factory=list)


@dataclass
class WorkspaceState:
    current: Optional[WorkspaceContent] = None
    history: List[WorkspaceContent] = field(default_factory=list)


class Module(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def produce_proposals(self, context: Dict[str, Any]) -> List[Proposal]:
        raise NotImplementedError

    def on_broadcast(self, content: WorkspaceContent, context: Dict[str, Any]) -> None:
        return None

    def tick(self, context: Dict[str, Any]) -> None:
        return None
