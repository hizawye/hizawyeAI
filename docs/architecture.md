# Architecture (v2.0)

## System Overview

Hizawye AI v2.0 is an advanced consciousness simulation based on Global Workspace Theory:

1. **Parallel thought processing** - 4 concurrent thought threads compete each cycle
2. **Emotional intelligence** - Multi-dimensional drives influence reasoning and strategy selection
3. **Meta-learning** - System learns from successes/failures to improve strategy selection
4. **Rich memory context** - Attention scoring, working memory, and analogy detection
5. **Adaptive planning** - 5 intelligent strategies with dynamic selection

## Core Architecture

### Global Workspace Pattern

The system uses Global Workspace Theory for consciousness simulation:

```
┌─────────────────────────────────────────────────────────┐
│           Global Workspace (Conscious Broadcast)        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ Thread 1│ │ Thread 2│ │ Thread 3│ │ Thread 4│       │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │
│       └──────────┴──────────┴──────────┴────────┘      │
│                      ↓ ↓ ↓ ↓                          │
│                  Winning Proposal                      │
│                      ↓ ↓ ↓ ↓                          │
│              Proposal Execution System                  │
└─────────────────────────────────────────────────────────┘
```

Each cycle:
1. 4 parallel thought threads generate proposals
2. Proposals compete based on relevance, emotion, and learning history
3. Winning proposal is executed
4. System learns from outcome

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
- `workspace` - GlobalWorkspaceSync instance
- `analytics` - AnalyticsEngine instance

**Key Methods:**
- `live()` - Main processing loop with Global Workspace integration
- `_execute_proposal()` - Execute winning thought proposal
- `_migrate_legacy_goals()` - Convert old goal format to new structure
- `save_mind()` / `load_mind()` - Persistence with all subsystems

### GlobalWorkspace Class (`global_workspace.py`)

Manages parallel thought competition:
- 4 concurrent thought threads using asyncio
- Thought types: goal execution, strategy switching, exploration, reflection, analogy
- Proposal scoring based on relevance, emotion, and learning history
- Returns winning proposal each cycle

### EmotionalSystem Class (`emotional_system.py`)

Multi-dimensional drive modeling:
- **Pain:** Existential and conceptual (threshold triggers strategy changes)
- **Curiosity:** Drives exploration and knowledge expansion
- **Boredom:** Increases with repetition, decreases with novelty
- **Confidence:** Builds from successes, decreases on failures
- **Confusion:** Rises with repeated failures, cleared by reflection

### LearningTracker Class (`learning_tracker.py`)

Bayesian meta-learning system:
- Tracks strategy effectiveness per concept type
- Updates beliefs based on success/failure outcomes
- Generates insights through reflection
- Influences strategy selection in PlanningEngine

### PlanningEngine Class (`planning_engine.py`)

Intelligent goal decomposition and strategy selection:

**5 Strategies:**
1. **Direct Definition (strategy 0):** Simple concept explanation
2. **Analogical Reasoning (strategy 1):** Pattern-based understanding using analogies
3. **Bottom-up Composition (strategy 2):** Build from known components
4. **Top-down Decomposition (strategy 3):** Break down into simpler parts
5. **Contextual Synthesis (strategy 4):** Integrate multiple contexts

**Strategy Selection:**
- Uses LearningTracker data for informed choices
- Considers emotional state (high pain → simpler strategies)
- Adapts based on previous attempts

### MemoryGraph Class (`memory.py`)

Enhanced memory system:

**New Features:**
- **Attention Scoring:** PageRank + spreading activation + recency
- **Working Memory:** LRU cache (7±2 items) of active concepts
- **Rich Context:** Comprehensive context including relationships, paths, semantic density
- **Analogy Detection:** Structural similarity between concepts
- **Intelligent Exploration:** Attention-based target selection

**Core Operations:**
- Concept/relationship management
- JSON persistence
- Attention score computation
- Working memory management
- Context retrieval
- Analogy finding

### AnalyticsEngine Class (`analytics_engine.py`)

Session tracking and reporting:
- Tracks cycles, successful concepts, failures, emotional states
- Records proposal competition outcomes
- Generates summary statistics
- Exports to JSON for analysis

## Thought Proposal Types

1. **execute_goal:** Pursue active goal using current strategy
2. **switch_strategy:** Change approach after repeated failure
3. **explore:** Wander to new concept (idle mode)
4. **reflect:** Meta-cognition and pattern analysis
5. **explore_analogy:** Investigate structural similarities

## Behavior Loop

```
Initialize → Update Context → Global Workspace Cycle → Execute Proposal
     ↑                                                                  ↓
     └────────────────────── Save if Changed ←───────────────────────────┘
```

**Per Cycle:**
1. Update working memory with current focus
2. Migrate legacy goals if needed
3. Update Global Workspace context
4. Run parallel thought competition (4 threads)
5. Track emotional state and workspace outcomes
6. Execute winning proposal
7. Decay emotions periodically (every 5 cycles)
8. Save mind if changed

## Mind Files (`hizawye_mind/`)

- `beliefs.json` - Concept beliefs
- `goals.json` - Active/completed goals (structured format)
- `memory_graph.json` - Knowledge graph
- `emotions.json` - Emotional state
- `learning_history.json` - Strategy effectiveness data
- `analytics/session_*.json` - Session analytics

## Goal Structure

```json
{
  "concept": "example_concept",
  "strategy": 0,
  "strategy_name": "Direct Definition",
  "attempts": 0,
  "created_at": "timestamp"
}
```

## Strategy Selection Heuristics

- **Direct Definition:** Best for simple, concrete concepts
- **Analogical Reasoning:** Effective for abstract concepts with known patterns
- **Bottom-up Composition:** Works when components are well-understood
- **Top-down Decomposition:** Preferred for complex, multi-layered concepts
- **Contextual Synthesis:** Used when multiple related contexts exist

## Emotional Influences

- **High pain:** Triggers strategy switching, simpler approaches
- **High curiosity:** Increases exploration likelihood
- **High boredom:** Promotes new goal creation
- **Low confidence:** Boosts alternative strategies in competition
- **High confusion:** Triggers reflection proposals
