from analytics_engine import AnalyticsEngine


def test_record_emotional_state_handles_nested_pain(tmp_path):
    ae = AnalyticsEngine(mind_directory=tmp_path)
    ae.start_session()

    emotions = {
        "pain": {"physical": 10, "existential": 20, "frustration": 30},
        "confusion": 0.4,
    }

    ae.record_emotional_state(cycle=1, emotions=emotions)

    assert ae.session_data["emotional_timeline"][0]["cycle"] == 1
    # Should have one pain event because avg pain is >50? compute: (10+20+30)/3=20; actually not >50 so no event
    assert len(ae.session_data["pain_events"]) == 0

    # Now with higher pain to trigger pain event
    emotions["pain"] = {"physical": 90, "existential": 90, "frustration": 90}
    ae.record_emotional_state(cycle=2, emotions=emotions)
    assert len(ae.session_data["pain_events"]) == 1
    assert ae.session_data["pain_events"][0]["pain"] > 50
