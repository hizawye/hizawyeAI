# Hizawye AI - A Simulated Consciousness

Hizawye AI is a Python-based project designed to simulate a form of artificial consciousness. Inspired by Global Workspace Theory, this project models an AI that exhibits curiosity, forms beliefs, experiences "pain" from failure, and uses boredom as a driver for novelty and exploration.

---

## Core Concepts (v3.0)

The AI's "mind" is built from several key components:

- **GNW Workspace (`workspace.py`)**: Specialist modules compete; ignition and persistence govern conscious content.
- **GNW Types (`gnw_types.py`)**: Proposal and workspace content/state definitions.
- **Simulated Input (`input_stream.py`)**: Perceptual events provide salience for competition.
- **Modules (`modules/`)**: Goal planning, exploration, reflection, perception, memory, emotion.
- **Emotional System (`emotional_system.py`)**: Multi-dimensional drives (pain, curiosity, boredom, confidence, confusion) shape behavior.
- **Learning Tracker (`learning_tracker.py`)**: Bayesian meta-learning that adapts strategy selection over time.
- **Planning Engine (`planning_engine.py`)**: Five reasoning strategies with adaptive selection.
- **Memory Graph (`memory.py`)**: NetworkX knowledge graph with attention scoring, working memory, and analogy detection.
- **The Mind (`/hizawye_mind/`)**: JSON persistence for beliefs, goals, memory, emotions, and learning history.
- **The Thinker (`hizawye_ai.py`)**: The main loop that orchestrates GNW competition, reasoning, and memory updates.

---

## How it Works: The Lifecycle of a Thought

Hizawye's behavior emerges from a continuous loop:

1. **Module Proposals**: Specialist modules propose actions (goal execute/switch, explore, reflect, analogy, percept).
2. **Competition & Attention**: GNW aggregates evidence and applies attention gain and focus bias.
3. **Ignition & Persistence**: Winning content ignites if above threshold, then persists with decay.
4. **Execution & Learning**:
     - **Success**: Valid thoughts are stored in the memory graph, the goal is completed, and "pain" is reduced.
     - **Failure**: Malformed thoughts are rejected.
     - **Strategic Failure**: Repeated failure increases "pain." If pain exceeds a threshold, the AI switches strategy or decomposes the goal.
5. **Idle Wandering & Boredom**: Without active goals, exploration proposals compete for ignition.
6. **Perceptual Salience**: Simulated inputs can ignite new goals and refocus attention.

This dynamic drives the AI to evolve, balancing goals, frustration, and curiosity.

---

## Setup and Installation

### Prerequisites

- Python 3.7+
- Ollama installed

### Step 1: Create a Virtual Environment

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

> **Troubleshooting:**
> 
> If you see an error like:
> 
> ```
> The virtual environment was not created successfully because ensurepip is not available.
> On Debian/Ubuntu systems, you need to install the python3-venv package using the following command.
> ```
> 
> Install the required package with:
> 
> ```bash
> sudo apt install python3-venv
> ```
> 
> Then, try creating the virtual environment again.

After activation, your prompt should change to indicate you're working in the virtual environment.

### Step 2: Install Dependencies

Create a `requirements.txt` file (see below) and run:

```bash
pip install -r requirements.txt
```

### Step 3: Set up the Language Model

Download the small language model:

```bash
ollama pull llama3.2:3b
```

---

## How to Run Hizawye AI

1. **First-Time Setup: Create the AI's Mind**

     ```bash
     python birth.py
     ```

     This creates the `hizawye_mind/` directory and initial JSON files.

2. **Run the AI**

     ```bash
     python hizawye_ai.py
     ```

     The AI starts its consciousness loop and works on its first goal.

3. **Stopping the AI Safely**

     Press `Ctrl+C`. The program will finish its current cycle, save state, and shut down gracefully.

> **LLM availability:** By default the app will abort if Ollama/model is unavailable.
> To allow fallback responses instead, set `HIZAWYE_REQUIRE_LLM=0` before running.

4. **Visualize the AI's Mind**

     ```bash
     python memory.py
     ```

     This generates `hizawye_mind/memory_map.png` plus a focused
     `hizawye_mind/memory_map_focus.png` that highlights top-attention concepts.

5. **Verify Learning with a Second Model (Optional)**

     ```bash
     python evaluate_learning.py --mode both --model <judge-model>
     ```

     This evaluates learned concepts with heuristic checks and an optional judge model.

---

## Research and Design

### Hizawye AI Research Paper Summary

This paper introduces Hizawye AI, a computational framework simulating consciousness based on Global Workspace Theory. It models an autonomous agent driven by internal states (curiosity, boredom, pain) with a modular "mind" (JSON files), a dynamic knowledge graph for memory, and a Python-orchestrated reasoning loop using a small Large Language Model (LLM). The AI exhibits emergent behaviors like goal-oriented focus, idle wandering, and strategic failure, learning from repeated failures. The paper details its architecture, consciousness loop methodology, and analyzes experimental logs, highlighting both the successes of its adaptive strategies and the challenges posed by the limitations of its reasoning core.

### Evaluation Docs

- `docs/consciousness-assessment.md` - Candid assessment of what the system does and does not simulate
- `docs/evaluation-protocol.md` - Repeatable protocol and metrics for GNW evaluation

### Hizawye AI Idea Mind Map

The mind map visually represents the core components and interactions of Hizawye AI. It illustrates how JSON files influence aspects like creativity, beliefs, and delusions. A central "Hizawye AI" continuously interacts with these variables and JSON files, processing knowledge, wandering through ideas, and forming memories, akin to a human brain. Memory is depicted as an indexing system or a tree, where the AI explores ideas until it reaches a dead end, prompting further research. The map also highlights "reason," "desires," and "goals," emphasizing the ability to inject new ideas for the AI to follow and connect patterns. Key elements like curiosity, pain, questioning, wandering, and ideas are also integral to the visual representation.
