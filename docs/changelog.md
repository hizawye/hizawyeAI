# Changelog

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

## [Unreleased]

### Changed
- LLM model: `tinyllama` → `llama3.2:3b` for improved reasoning quality
- Updated installation instructions in README
- Refreshed README to reflect v2.0 architecture and workflow

## [1.0.0] - Initial Release

### Features
- Memory graph-based knowledge system
- Goal-directed AI behavior (understanding, breakdown, expansion)
- Idle mode with boredom-driven exploration
- Mind persistence across sessions
- Signal handler for graceful shutdown

### Documentation
- README with research context and setup instructions
