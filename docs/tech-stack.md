# Tech Stack

## Language & Runtime

- **Python 3.x** - Primary language
- **Fedora Linux** - Development OS
- **Fish Shell** - Default shell

## Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| ollama | latest | Local LLM runtime and client |
| networkx | latest | Graph data structure for memory |
| matplotlib | latest | Visualization (future use) |

## AI Model

- **Model:** llama3.2:3b
- **Provider:** Ollama (local)
- **Download:** `ollama pull llama3.2:3b`
- **Use:** Concept reasoning, knowledge expansion

## Python Files

| File | Purpose |
|------|---------|
| `hizawye_ai.py` | Main AI implementation with GNW Workspace |
| `memory.py` | Enhanced memory graph with attention scoring |
| `log.py` | Logging setup |
| `birth.py` | Mind initialization |
| `wipe_memory.py` | Mind reset utility |
| `workspace.py` | GNW competition, ignition, and broadcast |
| `gnw_types.py` | Proposal and workspace type definitions |
| `input_stream.py` | Simulated input stream for perceptual salience |
| `modules/` | Specialist modules for proposals and broadcast updates |
| `emotional_system.py` | Multi-dimensional drive modeling |
| `learning_tracker.py` | Strategy effectiveness tracking |
| `planning_engine.py` | Goal decomposition and strategy selection |
| `analytics_engine.py` | Session metrics and reporting |
| `report_generator.py` | Analytics report generation |
| `analyze.py` | Command-line analytics tool |

## Data Persistence

- **Format:** JSON
- **Location:** `hizawye_mind/`
- **Files:**
  - `beliefs.json` - Concept beliefs
  - `goals.json` - Active/completed goals (structured format)
  - `memory_graph.json` - Knowledge graph
  - `emotional_state.json` - Emotional state
  - `strategy_history.json` - Strategy effectiveness data
  - `analytics/session_*.json` - Session analytics

## Development Tools

- **Git** - Version control
- **Neovim** - Code editor
- **venv** - Python virtual environment

## Architecture

- **Pattern:** Global Neuronal Workspace (GNW) inspired competition and ignition
- **Concurrency:** synchronous competition (no asyncio threads)
- **Memory Model:** NetworkX graph with attention mechanisms
- **Learning Model:** Bayesian updating of strategy effectiveness
