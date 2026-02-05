# Architecture (v3.0)

## System Overview

Hizawye AI v3.0 implements a Dehaene-style Global Neuronal Workspace (GNW) pattern:

1. **Specialist modules** generate proposals (goals, exploration, reflection, perception).
2. **Competition** aggregates evidence and applies attention gating.
3. **Ignition** occurs when a proposal exceeds threshold.
4. **Persistence** keeps workspace content active with decay.
5. **Broadcast** updates multiple modules each cycle.

## GNW Workspace Pattern

```
┌──────────────────────────────────────────────────────────┐
│                GNW Workspace (Ignition)                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐  │
│  │ Goals  │ │ Explore│ │Reflect │ │Percept │ │Memory  │  │
│  └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘  │
│      └─────────┴─────────┴─────────┴─────────┴────────┘  │
│                       ↓ Evidence/Salience                │
│                 Competition + Attention Gate             │
│                       ↓ Ignition                         │
│                Workspace Content + Persistence           │
│                       ↓ Broadcast                        │
│            Multiple Modules Update & Execute             │
└──────────────────────────────────────────────────────────┘
```

Each cycle:
1. Modules emit proposals (with evidence, salience, novelty, urgency).
2. Workspace aggregates evidence and scores proposals.
3. If the winner exceeds ignition threshold, it becomes conscious content.
4. Content persists with decay even without new ignition.
5. Broadcast updates modules and triggers execution.

## GWT Mapping (Operational)

This project uses a functional interpretation of Global Workspace Theory (GWT). The mapping below is intended as an operational checklist, not a claim of subjective experience.

- **Specialized processors** → `modules/` (goal planning, exploration, perception, reflection, memory, emotion)
- **Competition for access** → `workspace.py` scoring and selection
- **Ignition threshold** → `Workspace.ignition_threshold`
- **Global broadcast** → `Workspace._broadcast()` to all modules
- **Persistence/decay** → `Workspace._decay_and_persist()` activation decay
- **Behavioral impact** → `hizawye_ai.py` executes ignited content only

## Core Components

### HizawyeAI Class (`hizawye_ai.py`)

**State:**
- `beliefs` - Stored beliefs about concepts
- `goals` - Active and completed goals (structured format)
- `memory` - MemoryGraph instance
- `current_focus` - Currently active concept
- `emotions` - EmotionalSystem instance
- `learner` - LearningTracker instance
- `planner` - PlanningEngine instance
- `workspace` - GNW Workspace instance
- `analytics` - AnalyticsEngine instance

**Key Methods:**
- `live()` - Main processing loop with GNW workspace integration
- `_execute_workspace_content()` - Execute ignited content
- `_migrate_legacy_goals()` - Convert old goal format to new structure
- `save_mind()` / `load_mind()` - Persistence with all subsystems

### Workspace (`workspace.py`)

GNW core:
- Competition using evidence + salience + novelty + urgency
- Attention gain and focus bias
- Ignition threshold with persistence decay
- Broadcast to all modules each cycle

### GNW Types (`gnw_types.py`)

- `Proposal` - Module proposal with evidence metrics
- `WorkspaceContent` - Ignited or persistent content
- `WorkspaceState` - Current workspace + history
- `Module` - Specialist module interface

### Specialist Modules (`modules/`)

- `GoalPlannerModule` - Goal execution or strategy switching
- `ExplorationModule` - Idle exploration proposals
- `ReflectionModule` - Meta-cognitive reflection proposals
- `PatternRecognitionModule` - Analogy exploration proposals
- `PerceptionModule` - Simulated perceptual input proposals
- `MemoryModule` - Updates working memory on broadcast
- `EmotionModule` - Updates emotional state on broadcast

### Simulated Input (`input_stream.py`)

- `SimulatedInputStream` - Probabilistic event stream
- `InputEvent` - Event data and salience

### EmotionalSystem (`emotional_system.py`)

- Multi-dimensional drives (pain, curiosity, boredom, confidence, confusion)
- Produces drive vector used for attention gain and module proposals

### LearningTracker (`learning_tracker.py`)

- Bayesian-style tracking of strategy effectiveness
- Influences strategy selection in PlanningEngine

### PlanningEngine (`planning_engine.py`)

- 5 strategies (direct, analogy, bottom-up, top-down, synthesis)
- Uses emotional state + learning history for strategy selection

### MemoryGraph (`memory.py`)

- Attention scoring and working memory cache
- Rich context retrieval and analogy detection

### AnalyticsEngine (`analytics_engine.py`)

- Records competition outcomes and emotional timeline
- Tracks module wins and proposal frequency

## Workspace Content Types

1. `goal_execute` - Execute an active goal
2. `goal_switch` - Switch strategies after failure
3. `explore` - Explore a new concept
4. `reflect` - Meta-cognitive reflection
5. `analogy` - Explore analogies between concepts
6. `percept` - Process simulated perceptual input

## Behavior Loop

```
Initialize → Update Context → GNW Cycle → Execute Ignited Content
     ↑                                                     ↓
     └────────────────── Save if Changed ←─────────────────┘
```

**Per Cycle:**
1. Update working memory with current focus
2. Migrate legacy goals if needed
3. Update GNW context (including attention gain)
4. Run competition + ignition + persistence
5. Broadcast content to modules
6. Execute ignited content only
7. Decay emotions periodically (every 5 cycles)
8. Save mind if changed

## Mind Files (`hizawye_mind/`)

- `beliefs.json` - Concept beliefs
- `goals.json` - Active/completed goals (structured format)
- `memory_graph.json` - Knowledge graph
- `emotional_state.json` - Emotional state
- `strategy_history.json` - Strategy effectiveness data
- `analytics/session_*.json` - Session analytics

## Emotional Influences

- **High pain/confusion:** increases reflection proposals, simplifies strategies
- **High curiosity:** boosts exploration salience
- **High boredom:** increases exploration evidence
- **Low confidence:** reduces goal execution urgency
