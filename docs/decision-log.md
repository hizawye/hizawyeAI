# Decision Log

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
