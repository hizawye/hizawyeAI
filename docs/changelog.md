# Changelog

## [Unreleased]

### Added
- Analytics tracking for concept learning attempts (concepts learned + strategies used)
- Improved memory visualization: attention-based sizing, focus highlight, overview map (`memory_map_focus.png`)
- Behavior quality tuning: exploration gating, perception scaling under focus, repetition penalty
- Analytics tracking for ignition/persistence events and reflection triggers
- Consciousness assessment and evaluation protocol docs
- Ollama health check and fallback LLM responses when the model is unavailable
- Learning verification script with optional judge model (`evaluate_learning.py`)

### Changed
- LLM prompts tightened with stricter output rules and parsing safeguards

### Known Issues
- Observed 2026-02-04: system can enter a repeated `explore` loop where the mind wanders among concepts without executing goals

## [3.0.0] - 2026-02-04 - GNW Workspace

### Major Features
- GNW-style competition with evidence accumulation and attention gating
- Ignition threshold with persistence/decay dynamics
- Specialist modules for goals, exploration, reflection, perception, memory, and emotion
- Simulated perceptual input stream
- Broadcast-driven updates across modules

### New Modules
- `workspace.py` - GNW competition, ignition, persistence, and broadcast
- `gnw_types.py` - Proposal and workspace type definitions
- `input_stream.py` - Simulated input stream
- `modules/` - Specialist module implementations

### Changed
- `hizawye_ai.py` rewired to GNW workspace and module-based proposals
- Analytics competition tracking updated for GNW proposals

## [2.0.0] - 2026-02-04 - Advanced Consciousness

### Major Features
- Global Workspace Theory implementation with 4 parallel thought threads
- Multi-dimensional emotional system (pain, curiosity, boredom, confidence, confusion)
- Bayesian learning tracker for strategy adaptation
- 5 intelligent reasoning strategies:
  - Direct definition (concept explanation)
  - Analogical reasoning (pattern-based understanding)
  - Bottom-up composition (building from components)
  - Top-down decomposition (breaking down complex concepts)
  - Contextual synthesis (integrating multiple contexts)
- Meta-cognition and self-reflection capabilities
- Working memory cache (Miller's 7±2 limit)
- Attention scoring for memory nodes
- Analogy detection and pattern recognition
- Analytics engine with session tracking and reporting
- Rich context retrieval for memory concepts

### Enhanced Modules
- `memory.py` - Added attention scoring, working memory, analogy detection, rich context retrieval
- `hizawye_ai.py` - Refactored for Global Workspace integration, proposal execution system

### New Modules
- `global_workspace.py` - Parallel thought competition system
- `emotional_system.py` - Multi-dimensional drive modeling
- `learning_tracker.py` - Strategy effectiveness tracking
- `planning_engine.py` - Goal decomposition and strategy selection
- `analytics_engine.py` - Session metrics and reporting
- `report_generator.py` - Analytics report generation
- `analyze.py` - Command-line analytics tool

### Changed
- Goal structure: string-based → structured JSON with strategy tracking
- Mind persistence: Added emotional state and learning history
- Behavior: Sequential → parallel processing with winning proposal execution

### Backward Compatibility
- Legacy goals auto-migrate to new format
- Existing minds fully supported

## [1.0.0] - Initial Release

### Features
- Memory graph-based knowledge system
- Goal-directed AI behavior (understanding, breakdown, expansion)
- Idle mode with boredom-driven exploration
- Mind persistence across sessions
- Signal handler for graceful shutdown

### Documentation
- README with research context and setup instructions
