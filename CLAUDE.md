# Project: Hizawye AI

## 🛠 Tech Stack

- **Language:** Python
- **Environment:** Fedora Linux / Fish Shell
- **Core Dependencies:**
  - ollama - Local LLM runtime
  - networkx - Graph-based memory system
  - matplotlib - Visualization
- **Model:** llama3.2:3b (via Ollama)
- **Tools:** Git, Python venv

## 🧠 Automated Workflow

- **State Recovery:** On start, read `docs/project-status.md` and `docs/decision-log.md`.
- **Sync Command:** `/update-docs-and-commit`
  - Action: Update `docs/` -> `git add docs/` -> `git commit -m "docs: sync state"` -> `git add .` -> `git commit -m "feat: implementation"`

## ⚡ Commands

- **/context**: `cat docs/project-status.md docs/decision-log.md docs/architecture.md`
- **/status**: `cat docs/project-status.md`
- **/log**: `cat docs/decision-log.md | tail -n 20`

## 📦 Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Pull the model
ollama pull llama3.2:3b

# Initialize mind (first time only)
python birth.py

# Run AI
python hizawye_ai.py
```
