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
              ├── Tools (6 planned, 2 implemented)
              ├── Resources (4 planned, 1 implemented)
              └── Prompts (2 planned, 0 implemented)
```

### Core Metric: Context Health Score (CHS)

```
CHS = w₁·(1 - utilization_ratio) + w₂·relevance_score + w₃·(1 - redundancy_ratio) + w₄·coherence_score
```

Weights: `w₁=0.4, w₂=0.3, w₃=0.2, w₄=0.1`. Score is 0–100; status labels: HEALTHY (≥80), DEGRADING (≥50), CRITICAL (<50).

---

## Current Project State (as of Feb 17, 2026)

### ✅ Phase 1: Core Monitoring — COMPLETE

| File | Status | Purpose |
|------|--------|---------|
| `src/server.py` | ✅ Verified | FastMCP server with 2 tools + 1 resource. Inlined tool logic. |
| `src/core/tokenizer.py` | ✅ Verified | Token counting via `tiktoken` (cl100k_base fallback) |
| `src/core/scorer.py` | ✅ Verified | CHS calculation with weighted formula, status labels |
| `src/tools/metrics.py` | ✅ Verified | `get_token_metrics()` — token counts, utilization ratio, flags |
| `src/tools/analyze.py` | ✅ Verified | `analyze_context_health()` — composite score (Phase 1: utilization only) |
| `src/resources/health.py` | ✅ Verified | In-memory health state store with get/update |
| `tests/test_phase1.py` | ✅ 4/4 pass | Unit tests for tokenizer, scorer, metrics, analyze |
| `pyproject.toml` | ✅ Configured | Hatch build, uv-compatible, sentence-transformers in optional deps |
| `mcp.json` | ✅ Written | MCP server manifest |

**Verification results:**
- 4/4 unit tests pass (`uv run python -m pytest tests/ -v`)
- Server initializes with tools: `get_token_metrics`, `analyze_context_health`

### 🟡 What Remains

#### Phase 2 — Rot Detection
- [ ] Install `sentence-transformers` (`uv pip install -e ".[phase2]"`)
- [ ] Create `src/core/detector.py` — rot pattern detection engine
- [ ] Implement `score_relevance_decay` tool (embedding cosine similarity vs. original goal)
- [ ] Add redundancy detection (near-duplicate content finder)
- [ ] Build positional risk analysis ("Lost-in-the-Middle" detection)
- [ ] Implement `detect_context_rot` tool (multi-signal analysis)
- [ ] Create `rot://alerts/active` resource + `src/resources/alerts.py`

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
| LLM | Google Gemini (`google-genai`) | ✅ Installed (unused until Phase 3) |
| Embeddings | `sentence-transformers` | ❌ Optional dep, Phase 2 |
| Token Counting | `tiktoken` | ✅ Installed & used |
| Vector Similarity | NumPy | ✅ Installed (unused until Phase 2) |
| Storage | In-memory (SQLite planned Phase 3) | 🟡 In-memory only |
| Transport | STDIO | 🟡 HTTP planned Phase 4 |
| Package Manager | `uv` | ✅ Active |

---

## File Tree

```
context-rot-monitor/
├── src/
│   ├── __init__.py
│   ├── server.py              # MCP entry point (FastMCP, 2 tools, 1 resource)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── tokenizer.py       # tiktoken wrapper
│   │   └── scorer.py          # CHS calculation
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── metrics.py         # get_token_metrics logic
│   │   └── analyze.py         # analyze_context_health logic
│   ├── resources/
│   │   ├── __init__.py
│   │   └── health.py          # rot://health/current state
│   └── prompts/
│       └── __init__.py        # (empty — Phase 3)
├── tests/
│   ├── __init__.py
│   └── test_phase1.py         # 4 unit tests (all passing)
├── pyproject.toml              # uv + hatch config
├── mcp.json                    # MCP manifest
├── HANDOVER.md                 # Full architecture spec
├── README.md                   # Usage docs
└── gemini.md                   # This file
```

---

## How to Run

```bash
# Install (editable, Phase 1 only)
uv pip install -e .

# Install with Phase 2 deps (sentence-transformers + torch)
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
2. **Lightweight Phase 1** — Only token utilization; no heavy ML deps
3. **In-memory first** — SQLite deferred to Phase 3
4. **FastMCP** — High-level API for cleaner tool/resource registration
5. **Absolute imports** — All files use `from src.` imports, package installed via `uv pip install -e .`
6. **`sentence-transformers` optional** — Avoids 108MB PyTorch download until Phase 2
