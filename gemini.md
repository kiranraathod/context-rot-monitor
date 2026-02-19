# Agentic Context Rot Monitor — Project Context

> **For AI assistants (Gemini CLI, Cloud Code, Codex).** This file provides full project context for onboarding.

---

## What This Project Is

An **MCP (Model Context Protocol) Server** that monitors, scores, and remediates **context degradation** ("context rot") in LLM agent systems. Context rot is the silent performance decline that occurs as an agent's context window fills with irrelevant, redundant, or diluted information across multi-step execution.

**Origin:** Extended from the [Context-Engineering-for-Multi-Agent-Systems](https://github.com/Denis2054/Context-Engineering-for-Multi-Agent-Systems) book (Packt, Denis Rothman).

---

## Architecture Overview

```
MCP Host (Claude, VS Code, Cursor, Gemini CLI, Codex)
  └── MCP Client (JSON-RPC 2.0 over STDIO or HTTP)
        └── Context Rot Monitor Server
              ├── Tools (6 planned, 3 implemented)
              ├── Resources (4 planned, 2 implemented)
              └── Prompts (2 planned, 0 implemented)
```

### Core Metric: Context Health Score (CHS)

```
CHS = w₁·(1 - utilization_ratio) + w₂·relevance_score + w₃·(1 - redundancy_ratio) + w₄·coherence_score
```

Weights: `w₁=0.4, w₂=0.3, w₃=0.2, w₄=0.1`. Score is 0–100; status labels: HEALTHY (≥80), DEGRADING (≥50), CRITICAL (<50).

---

## Current Project State (as of Feb 18, 2026)

### ✅ Phase 1: Core Monitoring — COMPLETE & VERIFIED
- **Metric**: Token Utilization
- **Tools**: `get_token_metrics`, `analyze_context_health`
- **Resource**: `rot://health/current`
- **Status**: Fully implemented, tested, and integrated.

### ✅ Phase 2: Rot Detection — COMPLETE & VERIFIED
- **Metric**: Semantic Relevance + Redundancy
- **Tools**: 
    - `detect_context_rot`: Deep-dive analysis (Relevance, Redundancy, Positional Risk)
    - `analyze_context_health`: Updated to use real semantic scores when `goal` is provided.
- **Resource**: `rot://alerts/active` (Auto-alerts on drift/redundancy)
- **Logic**: `ContextRotDetector` using `sentence-transformers` (all-MiniLM-L6-v2) for embedding-based analysis.

### 🟡 What Remains

#### Phase 3 — Remediation
- [ ] Implement `recommend_pruning` tool
- [ ] Implement `summarize_context` tool (LLM-powered compression via Gemini)
- [ ] Build configurable alert threshold system
- [ ] Create `diagnose_rot` and `optimize_context` prompt templates
- [ ] Create `rot://metrics/history` resource + `src/resources/history.py`
- [ ] Create `src/storage/metrics_store.py` (SQLite persistence)

#### Phase 4 — Production Polish
- [ ] Add Streamable HTTP transport
- [ ] Publish to MCP registry + PyPI
- [ ] Record demo video

---

## Tech Stack

| Layer | Choice | Status |
|-------|--------|--------|
| MCP SDK | `mcp` (FastMCP) | ✅ Installed & used |
| LLM | Google Gemini (`google-genai`) | ✅ Installed (aiming for Phase 3) |
| Embeddings | `sentence-transformers` | ✅ Installed & used (Phase 2) |
| Token Counting | `tiktoken` | ✅ Installed & used |
| Vector Similarity | `scikit-learn` | ✅ Installed & used (Phase 2) |
| Storage | In-memory (SQLite planned Phase 3) | 🟡 In-memory only |
| Transport | STDIO | 🟡 HTTP planned Phase 4 |
| Package Manager | `uv` | ✅ Active |

---

## File Tree

```
context-rot-monitor/
├── src/
│   ├── __init__.py
│   ├── server.py              # MCP entry point (FastMCP, 3 tools, 2 resources)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── tokenizer.py       # tiktoken wrapper
│   │   ├── scorer.py          # CHS calculation
│   │   └── detector.py        # Rot detection logic (embeddings/redundancy)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── metrics.py         # get_token_metrics logic
│   │   ├── analyze.py         # analyze_context_health logic
│   │   └── detect.py          # detect_context_rot logic
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── health.py          # rot://health/current state
│   │   └── alerts.py          # rot://alerts/active state
│   └── prompts/
│       └── __init__.py        # (empty — Phase 3)
├── tests/
│   ├── __init__.py
│   ├── test_phase1.py         # Unit tests for Phase 1
│   └── test_phase2.py         # Unit tests for Phase 2
├── pyproject.toml              # uv + hatch config
├── mcp.json                    # MCP manifest
├── HANDOVER.md                 # Full architecture spec
├── README.md                   # Usage docs
└── gemini.md                   # This file
```

---

## How to Run

```bash
# Install with all dependencies (Phase 1 + 2)
uv pip install -e ".[phase2]"

# Run tests
uv run python -m pytest tests/ -v

# Verify server loads
uv run python -c "from src.server import mcp; print(mcp.name)"

# Run MCP server (STDIO transport)
uv run python -m src.server
```

---

## CLI Compatibility

| CLI | MCP Support | Transport | Config |
|-----|-------------|-----------|--------|
| **Gemini CLI** | ✅ Native | STDIO, SSE, HTTP | `settings.json` |
| **OpenAI Codex** | ✅ Native | STDIO, HTTP | `~/.codex/config.toml` |
| **Cloud Code** | ✅ Via Gemini Code Assist | STDIO | IDE plugin settings |
| **Claude Desktop** | ✅ Native | STDIO | `claude_desktop_config.json` |
| **Cursor** | ✅ Native | STDIO | Settings UI |

---

## Key Design Decisions

1. **Provider-agnostic LLM** — Gemini default, easily swappable
2. **Phase 2 Intelligence** — Uses `sentence-transformers` for local, fast semantic analysis (no API costs).
3. **In-memory first** — SQLite deferred to Phase 3
4. **FastMCP** — High-level API for cleaner tool/resource registration
5. **Absolute imports** — All files use `from src.` imports, package installed via `uv pip install -e .`
