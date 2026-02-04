import random

from memory import MemoryGraph


def test_attention_scores_prioritize_focus(tmp_path):
    mg = MemoryGraph(mind_directory=str(tmp_path))
    mg.add_node("a")
    mg.add_node("b")
    mg.add_connection("a", "b")
    mg.update_working_memory("a")

    scores = mg.compute_attention_scores(current_focus="a")

    assert scores["a"] > scores["b"]
    # Ensure recency contributes (working-memory focus should have high score)
    assert scores["a"] >= 0.5


def test_working_memory_eviction_respects_capacity(tmp_path):
    mg = MemoryGraph(mind_directory=str(tmp_path))
    for idx in range(8):
        mg.update_working_memory(f"c{idx}")

    wm = mg.get_working_memory_concepts()
    assert len(wm) == mg.working_memory_capacity
    assert "c0" not in wm
    assert wm[0] == "c7"  # most recently added


def test_find_exploration_target_prefers_non_recent_unknowns(tmp_path):
    random.seed(0)  # make any fallback randomness deterministic
    mg = MemoryGraph(mind_directory=str(tmp_path))
    mg.add_node("a")
    mg.add_node("b", {"description": "known concept"})
    mg.add_node("c")  # unknown concept preferred
    mg.add_connection("a", "b")
    mg.add_connection("a", "c")

    mg.update_working_memory("b")
    mg.update_working_memory("a")

    target = mg.find_exploration_target(current_focus="a", avoid_recent=True)
    assert target == "c"
