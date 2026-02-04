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

## 2026-02-04 - Project Initialization

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
