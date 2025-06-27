# Hizawye AI - A Simulated Consciousness

Hizawye AI is a Python-based project designed to simulate a form of artificial consciousness. Inspired by the Global Workspace Theory and an initial conceptual diagram, this project models an AI that exhibits curiosity, forms beliefs, experiences "pain" from failure, and uses boredom as a driver for novelty and exploration.

---

## Core Concepts

The AI's "mind" is built from several key components:

- **The Mind (`/hizawye_mind/`)**: Directory containing JSON files representing the AI's internal state:
    - `state.json`: Dynamic values like curiosity, boredom, and pain.
    - `beliefs.json`: The AI's core "truths" about itself and the world.
    - `goals.json`: List of active and completed objectives.
    - `memory_graph.json`: The AI's entire memory network.
- **The Memory (`memory.py`)**: A knowledge graph (using `networkx`) representing the AI's understanding. Concepts (nodes) are connected by relationships (edges), and can hold descriptions.
- **The Thinker (`hizawye_ai.py`)**: The main processing loop. Reads state, directs focus, and uses a local LLM to reason, synthesize ideas, and form memories.

---

## How it Works: The Lifecycle of a Thought

Hizawye's behavior emerges from a continuous loop:

1. **Goal-Oriented Focus**: The AI prioritizes its active goal (e.g., "Deepen understanding of 'philosophy'").
2. **Reasoning**: Uses a local LLM (`ollama` with `tinyllama`) to achieve its goal by prompting for definitions or breakdowns.
3. **Validation & Learning**:
     - **Success**: Valid thoughts are stored in the memory graph, the goal is completed, and "pain" is reduced.
     - **Failure**: Malformed thoughts are rejected.
     - **Strategic Failure**: Repeated failure increases "pain." If pain exceeds a threshold, the AI abandons the current approach, breaks the goal into sub-goals, and tries again.
4. **Idle Wandering & Boredom**: Without active goals, the AI wanders its memory graph, increasing boredom.
5. **Novelty Seeking**: High boredom triggers the creation of a new goal to expand knowledge, restarting the learning cycle.

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
ollama pull tinyllama
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

4. **Visualize the AI's Mind**

     ```bash
     python memory.py
     ```

     This displays the current memory graph without modifying any data.

---

## Research and Design

### Hizawye AI Research Paper Summary

This paper introduces Hizawye AI, a computational framework simulating consciousness based on Global Workspace Theory. It models an autonomous agent driven by internal states (curiosity, boredom, pain) with a modular "mind" (JSON files), a dynamic knowledge graph for memory, and a Python-orchestrated reasoning loop using a small Large Language Model (LLM). The AI exhibits emergent behaviors like goal-oriented focus, idle wandering, and strategic failure, learning from repeated failures. The paper details its architecture, consciousness loop methodology, and analyzes experimental logs, highlighting both the successes of its adaptive strategies and the challenges posed by the limitations of its reasoning core.

### Hizawye AI Idea Mind Map

The mind map visually represents the core components and interactions of Hizawye AI. It illustrates how JSON files influence aspects like creativity, beliefs, and delusions. A central "Hizawye AI" continuously interacts with these variables and JSON files, processing knowledge, wandering through ideas, and forming memories, akin to a human brain. Memory is depicted as an indexing system or a tree, where the AI explores ideas until it reaches a dead end, prompting further research. The map also highlights "reason," "desires," and "goals," emphasizing the ability to inject new ideas for the AI to follow and connect patterns. Key elements like curiosity, pain, questioning, wandering, and ideas are also integral to the visual representation.