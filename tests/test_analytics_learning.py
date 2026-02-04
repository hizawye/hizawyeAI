from analytics_engine import AnalyticsEngine


def test_record_concept_learned_tracks_attempts_and_strategies(tmp_path):
    ae = AnalyticsEngine(mind_directory=tmp_path)
    ae.start_session()

    ae.record_concept_learned(
        concept="concept_a",
        strategy="direct_define",
        success=False,
        pain_cost=10.0,
        attempts=1,
    )

    ae.record_concept_learned(
        concept="concept_a",
        strategy="direct_define",
        success=True,
        pain_cost=-5.0,
        attempts=2,
    )

    concepts = ae.session_data["concepts_learned"]
    assert "concept_a" in concepts
    assert concepts["concept_a"]["attempts"] == 3
    assert concepts["concept_a"]["success"] is True

    strategies = ae.session_data["strategies_used"]
    assert "direct_define" in strategies
    assert strategies["direct_define"]["attempts"] == 3
    assert strategies["direct_define"]["successes"] == 1
