# AGENTS.md - Codex Operating Guide

This file tailors Codex behavior for this repo. It is based on `CLAUDE.md` but adapted for Codex.

## Project Summary

Hizawye AI is a Python project simulating artificial consciousness using Global Workspace Theory. The system combines parallel thought threads, emotional drives, meta-learning, and a graph-based memory.

## Tech Stack

- Language: Python
- Environment: Fedora Linux / Fish Shell
- Core dependencies:
  - ollama (local LLM runtime)
  - networkx (graph memory)
  - matplotlib (visualization)
- Model: `llama3.2:3b` (via Ollama)
- Tools: Git, Python venv

## Repo Navigation

- Core loop: `hizawye_ai.py`
- Global Workspace: `global_workspace.py`
- Emotions: `emotional_system.py`
- Learning tracker: `learning_tracker.py`
- Planning: `planning_engine.py`
- Memory graph: `memory.py`
- Analytics: `analytics_engine.py`, `report_generator.py`, `analyze.py`
- Mind state (JSON): `hizawye_mind/`
- Docs: `docs/`

## Documentation Workflow

- On start, read:
  - `docs/project-status.md`
  - `docs/decision-log.md`
  - `docs/architecture.md`
- Keep these docs aligned with any significant changes.
- When asked to “update docs,” prefer:
  1. Update `docs/project-status.md` (current state + next steps)
  2. Update `docs/decision-log.md` (new decisions with date)
  3. Update `docs/changelog.md` (user-facing change notes)
  4. Update `README.md` if public overview changed

## Common Commands

- Context: `cat docs/project-status.md docs/decision-log.md docs/architecture.md`
- Status: `cat docs/project-status.md`
- Decision tail: `cat docs/decision-log.md | tail -n 20`

## Setup & Run

```bash
pip install -r requirements.txt
ollama pull llama3.2:3b
python birth.py
python hizawye_ai.py
```

## Commit Guidance

- If only docs changed, use `docs:` prefix.
- If implementation changes, use `feat:` or `fix:` as appropriate.
- Avoid bundling unrelated changes (especially logs) into a commit.
