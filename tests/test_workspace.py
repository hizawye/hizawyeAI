from gnw_types import Proposal
from workspace import Workspace


class StaticModule:
    def __init__(self, proposals):
        self.name = "Static"
        self._proposals = proposals

    def produce_proposals(self, context):
        return list(self._proposals)

    def on_broadcast(self, content, context):
        return None

    def tick(self, context):
        return None


def test_workspace_ignition_occurs_with_high_score():
    proposal = Proposal(
        source="Test",
        content={"type": "goal_execute", "payload": {}},
        evidence=1.0,
        salience=1.0,
        novelty=0.5,
        urgency=0.5,
    )
    ws = Workspace([StaticModule([proposal])], ignition_threshold=0.5, noise=0.0)
    ws.update_context(attention_gain=1.0)

    content = ws.cycle()

    assert content is not None
    assert content.ignited is True
    assert content.type == "goal_execute"


def test_workspace_persistence_when_no_new_ignition():
    proposal = Proposal(
        source="Test",
        content={"type": "explore", "payload": {"target_concept": "x"}},
        evidence=1.0,
        salience=1.0,
        novelty=0.5,
        urgency=0.5,
    )
    module = StaticModule([proposal])
    ws = Workspace(
        [module],
        ignition_threshold=0.6,
        persistence_threshold=0.2,
        decay_rate=0.9,
        noise=0.0,
    )
    ws.update_context(attention_gain=1.0)

    first = ws.cycle()
    assert first is not None and first.ignited is True

    module._proposals = []
    persisted = ws.cycle()

    assert persisted is not None
    assert persisted.ignited is False
    assert persisted.type == "explore"


def test_attention_gain_controls_ignition_threshold():
    proposal = Proposal(
        source="Test",
        content={"type": "reflect", "payload": {}},
        evidence=0.9,
        salience=0.9,
        novelty=0.1,
        urgency=0.1,
    )
    ws = Workspace([StaticModule([proposal])], ignition_threshold=0.7, noise=0.0)

    ws.update_context(attention_gain=0.5)
    assert ws.cycle() is None

    ws.update_context(attention_gain=1.2)
    content = ws.cycle()
    assert content is not None
    assert content.ignited is True
