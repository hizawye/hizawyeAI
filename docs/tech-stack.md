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
| `hizawye_ai.py` | Main AI implementation |
| `memory.py` | Memory graph system |
| `log.py` | Logging setup |
| `birth.py` | Mind initialization |
| `wipe_memory.py` | Mind reset utility |

## Data Persistence

- **Format:** JSON
- **Location:** `hizawye_mind/`
- **Files:** state.json, goals.json, beliefs.json, memory_graph.json

## Development Tools

- **Git** - Version control
- **Neovim** - Code editor
- **venv** - Python virtual environment
