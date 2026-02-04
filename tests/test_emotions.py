from emotional_system import EmotionalSystem


def test_drive_vector_defaults_are_consistent(tmp_path):
    es = EmotionalSystem(mind_directory=str(tmp_path / "mind"))
    drives = es.compute_drive_vector()

    assert set(drives.keys()) >= {
        "exploration",
        "focus",
        "retreat",
        "temperature",
        "should_simplify",
        "should_explore",
    }
    assert 0.1 <= drives["temperature"] <= 1.0


def test_modulate_prompt_adds_simplify_when_confused(tmp_path):
    es = EmotionalSystem(mind_directory=str(tmp_path / "mind"))
    es.state["pain"]["frustration"] = 80
    es.state["confusion"] = 0.8

    prompt = es.modulate_llm_prompt("Explain this", context_type="general")
    assert "Explain in the simplest" in prompt
    assert "analogies and examples" in prompt


def test_emotional_updates_change_confidence_and_frustration(tmp_path):
    es = EmotionalSystem(mind_directory=str(tmp_path / "mind"))
    es.state["pain"]["frustration"] = 10
    es.state["confidence"] = 0.5
    es.state["confusion"] = 0.2

    es.update_on_failure(repeated=True)
    confidence_after_failure = es.state["confidence"]
    assert es.state["pain"]["frustration"] > 10
    assert es.state["confidence"] < 0.5
    assert es.state["confusion"] > 0.2

    es.update_on_success(difficulty=2.0)
    assert es.state["pain"]["frustration"] < 35  # should have decreased from failure bump
    assert es.state["confidence"] > confidence_after_failure
