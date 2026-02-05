# Decision Log

## 2026-02-05 - Learning Analytics + Visualization Upgrade

**Decision:** Record concept learning outcomes in analytics and improve memory visualization.

**Rationale:**
- Session summaries showed `0/0` concepts learned without explicit tracking
- Visualization needed focus and attention cues for interpretability

**Key Components:**
- `hizawye_ai.py` - Record concept learning attempts in analytics
- `memory.py` - Attention-based sizing, focus highlight, and top-attention map

## 2026-02-05 - Goal Execution Priority + Goal Dedupe

**Decision:** Boost goal execution proposals and prevent duplicate goals from piling up.

**Rationale:**
- Workspace competition was dominated by percepts, starving goal execution
- Percepts repeatedly created duplicate goals for the same concepts

**Key Components:**
- `modules/goal_planner_module.py` - Add baseline evidence/salience/urgency for goal proposals
- `hizawye_ai.py` - Skip creating duplicate goals; remove duplicates after a concept succeeds

## 2026-02-05 - Workspace Ignition Metrics + Reflection Logging

**Decision:** Record ignition/persistence metrics and reflection events in analytics for evaluation.

**Rationale:**
- Needed objective measures to compare GNW dynamics across runs
- Reflections were not visible in analytics reports

**Key Components:**
- `analytics_engine.py` - Track ignition, persistence runs, activation stats
- `hizawye_ai.py` - Record workspace events and reflection outcomes
- `report_generator.py` - Include ignition/persistence metrics in reports

## 2026-02-05 - LLM Health Check + Fallback Responses

**Decision:** Add an Ollama health check and deterministic fallback responses when LLM calls fail.

**Rationale:**
- Prevent silent "I feel disconnected" failures from stalling learning
- Provide actionable error guidance when Ollama is not running or model is missing

**Key Components:**
- `hizawye_ai.py` - LLM availability check and fallback response generator

## 2026-02-05 - External Learning Verification Script

**Decision:** Add a script to verify learned concepts using heuristics and an optional judge model.

**Rationale:**
- Need independent verification of learning quality beyond internal success flags
- Support a second model as a judge for stronger evaluation

**Key Components:**
- `evaluate_learning.py` - Evaluates learned concepts and produces reports

## 2026-02-04 - GNW Refactor: Ignition + Specialist Modules

**Decision:** Replace the fixed-thread Global Workspace with a GNW-style workspace.

**Rationale:**
- GNW provides ignition, persistence, and broadcast dynamics closer to modern GWT variants
- Specialist modules enable evidence accumulation and attention gating
- Simulated input stream introduces perceptual salience for competition

**Key Components:**
- `workspace.py` - GNW competition, ignition, persistence, and broadcast
- `gnw_types.py` - Proposal and workspace content/state definitions
- `input_stream.py` - Simulated perceptual input
- `modules/` - Specialist modules for goals, exploration, reflection, perception, memory, emotion

**Files Changed:**
- `hizawye_ai.py` - Rewired to GNW workspace and module execution
- `analytics_engine.py` - Competition tracking updated for GNW proposals
- Docs updated for GNW architecture

## 2026-02-04 - Model Upgrade: tinyllama → llama3.2:3b

**Decision:** Switch LLM model from `tinyllama` to `llama3.2:3b`

**Rationale:**
- Llama 3.2 (3B) is a more capable model with improved reasoning
- Better quality responses for concept definitions and knowledge expansion
- Still small enough to run locally with reasonable performance
- Updated in both codebase (`hizawye_ai.py:73`) and documentation (`README.md`)

**Files Changed:**
- `hizawye_ai.py:73` - Model reference in reason_with_llm()
- `README.md:26` - Installation instructions

## 2026-02-04 - Advanced Consciousness Architecture (v2.0)

**Decision:** Transform single-threaded system into parallel, adaptive consciousness engine

**Rationale:**
- Original architecture was too rigid with fixed goal types and sequential processing
- Implemented Global Workspace Theory for consciousness simulation
- Added emotional intelligence to drive learning and adaptation
- Built meta-learning system to improve strategy selection over time
- Enhanced memory with attention mechanisms and analogy detection

**Key Components:**
- `global_workspace.py` - 4 parallel thought threads competing each cycle
- `emotional_system.py` - Multi-dimensional drives (pain, curiosity, boredom, confidence, confusion)
- `learning_tracker.py` - Bayesian tracking of strategy effectiveness
- `planning_engine.py` - 5 intelligent strategies with adaptive selection
- `analytics_engine.py` - Session tracking and reporting
- Enhanced `memory.py` - Attention scoring, working memory, rich context retrieval

**Files Changed:**
- `hizawye_ai.py` - Refactored to use Global Workspace, added proposal execution system
- `memory.py` - Added attention scoring, working memory, analogy detection, rich context
- New modules: `global_workspace.py`, `emotional_system.py`, `learning_tracker.py`, `planning_engine.py`, `analytics_engine.py`, `report_generator.py`, `analyze.py`

**Backward Compatibility:**
- Legacy string goals auto-migrate to structured format
- All original functionality preserved with enhanced intelligence

## 2026-02-04 - Model Upgrade: tinyllama → llama3.2:3b

**Decision:** Initialize documentation structure

**Rationale:**
- Establish project documentation standards
- Track architectural decisions over time
- Enable state recovery between sessions

**Files Created:**
- `docs/project-status.md` - Current state and next steps
- `docs/decision-log.md` - Architectural decisions
- `docs/architecture.md` - System design
- `docs/tech-stack.md` - Technical stack
- `docs/changelog.md` - Version history
- `CLAUDE.md` - Project-specific AI instructions
