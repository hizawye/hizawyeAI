# Architecture

## System Overview

Hizawye AI is a goal-directed autonomous agent that:

1. **Maintains a memory graph** of concepts and relationships (networkx)
2. **Sets and pursues goals** to deepen understanding
3. **Reasons using a local LLM** (Ollama with llama3.2:3b)
4. **Persists its "mind"** across sessions (JSON files)

## Core Components

### HizawyeAI Class (`hizawye_ai.py`)

**State:**
- `state` - Internal state (boredom, pain levels)
- `beliefs` - Stored beliefs about concepts
- `goals` - Active and completed goals
- `memory` - MemoryGraph instance
- `current_focus` - Currently active concept

**Key Methods:**
- `live()` - Main processing loop
- `reason_with_llm()` - Query LLM for thoughts
- `save_mind()` / `load_mind()` - Persistence

### MemoryGraph Class (`memory.py`)

- Graph-based knowledge store (networkx)
- Concepts as nodes, relationships as edges
- JSON persistence

### Mind Files (`hizawye_mind/`)

- `state.json` - Current state values
- `goals.json` - Active/completed goals
- `beliefs.json` - Concept beliefs
- `memory_graph.json` - Knowledge graph

## Behavior Loop

1. Check for active goals
2. If goal exists:
   - Extract concept from goal
   - Execute goal type (Deepen understanding / Break down / Expand knowledge)
   - Validate response
   - Update memory/state
3. If no goals (idle mode):
   - Check boredom threshold
   - Wander memory graph
   - Create new goals if needed
4. Save mind if changed
5. Repeat

## Goal Types

- **Deepen understanding**: Define a concept concisely
- **Break down**: Decompose concept into sub-concepts
- **Expand knowledge**: Discover related new concepts
