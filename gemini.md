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

### ✅ What Exists (Phase 1 — Partial)

| File | Status | Purpose |
|------|--------|---------|
| `src/core/tokenizer.py` | ✅ Written | Token counting via `tiktoken` (cl100k_base fallback) |
| `src/core/scorer.py` | ✅ Written | CHS calculation with weighted formula, status labels |
| `src/tools/metrics.py` | ✅ Written | `get_token_metrics()` — token counts, utilization ratio |
| `src/tools/analyze.py` | ✅ Written | `analyze_context_health()` — composite score (Phase 1: utilization only) |
| `src/resources/health.py` | ✅ Written | In-memory health state store with get/update |
| `src/server.py` | ✅ Written | FastMCP server with 2 tools + 1 resource registered |
| `tests/test_phase1.py` | ✅ Written | Unit tests for tokenizer, scorer, metrics, analyze |
| `pyproject.toml` | ✅ Written | Project metadata and dependencies |
| `mcp.json` | ✅ Written | MCP server manifest |
| `README.md` | ✅ Written | Basic usage documentation |
| `HANDOVER.md` | ✅ Written | Full architecture spec and roadmap |

### 🔴 Critical Issues Blocking Execution

1. **Missing `__init__.py` files** — No `__init__.py` in `src/`, `src/core/`, `src/tools/`, `src/resources/`, `src/prompts/`, or `tests/`. Python cannot treat these as packages.
2. **Broken imports in `server.py`** — Uses `from src.tools.metrics import ...` (absolute). Should use relative imports or the project must be installed as a package.
3. **Unused import in `metrics.py`** — `from mcp.server.fastmcp import FastMCP` is imported but never used.
4. **`sentence-transformers` not installed** — Listed in `pyproject.toml` but deferred during setup (it pulls PyTorch ~108MB). Not needed until Phase 2.
5. **No `src/storage/` directory** — `HANDOVER.md` specifies `src/storage/metrics_store.py` but directory doesn't exist.
6. **No `src/core/detector.py`** — Planned rot pattern detection engine not created yet.

### 🟡 What Remains (by Phase)

#### Phase 1 — Fix & Verify (immediate)
- [ ] Add `__init__.py` files to all packages
- [ ] Fix import paths in `server.py` (use relative imports consistently)
- [ ] Remove unused `FastMCP` import from `metrics.py`
- [ ] Run and pass unit tests
- [ ] Verify MCP server starts via `mcp run src/server.py`

#### Phase 2 — Rot Detection
- [ ] Install `sentence-transformers` for embedding-based relevance scoring
- [ ] Create `src/core/detector.py` — rot pattern detection engine
- [ ] Implement `score_relevance_decay` tool (embedding cosine similarity vs. original goal)
- [ ] Add redundancy detection (near-duplicate content finder)
- [ ] Build positional risk analysis ("Lost-in-the-Middle" detection)
- [ ] Implement `detect_context_rot` tool (multi-signal analysis)
- [ ] Create `rot://alerts/active` resource
- [ ] Create `src/resources/alerts.py`

#### Phase 3 — Remediation
- [ ] Implement `recommend_pruning` tool
- [ ] Implement `summarize_context` tool (LLM-powered compression via Gemini)
- [ ] Build configurable alert threshold system
- [ ] Create `diagnose_rot` and `optimize_context` prompt templates
- [ ] Create `rot://metrics/history` resource + `src/resources/history.py`
- [ ] Create `src/storage/metrics_store.py` (SQLite persistence)

#### Phase 4 — Production Polish
- [ ] Add Streamable HTTP transport
- [ ] Publish to MCP registry
- [ ] Publish to PyPI
- [ ] Record demo video

---

## Tech Stack

| Layer | Choice | Status |
|-------|--------|--------|
| MCP SDK | `mcp` (official Python SDK via `FastMCP`) | ✅ Installed |
| LLM | Google Gemini (`google-genai`) | ✅ Installed (unused yet) |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) | ❌ Not installed |
| Token Counting | `tiktoken` | ✅ Installed & used |
| Vector Similarity | NumPy cosine similarity | ✅ Installed (unused yet) |
| Storage | SQLite / in-memory | 🟡 In-memory only |
| Transport | STDIO (primary) + Streamable HTTP (planned) | 🟡 STDIO only |
| Package Manager | `uv` | ✅ Used for venv + pip |

---

## File Tree

```
context-rot-monitor/
├── src/
│   ├── server.py              # MCP server entry point (FastMCP)
│   ├── core/
│   │   ├── tokenizer.py       # tiktoken wrapper
│   │   └── scorer.py          # CHS calculation
│   ├── tools/
│   │   ├── metrics.py         # get_token_metrics tool logic
│   │   └── analyze.py         # analyze_context_health tool logic
│   ├── resources/
│   │   └── health.py          # rot://health/current state store
│   └── prompts/               # (empty — Phase 3)
├── tests/
│   └── test_phase1.py         # Unit tests for Phase 1
├── pyproject.toml              # Project config
├── mcp.json                    # MCP manifest
├── HANDOVER.md                 # Full architecture spec
├── README.md                   # Usage docs
└── gemini.md                   # This file
```

---

## How to Run (once issues are fixed)

```bash
# Install dependencies
uv venv && uv pip install -e .

# Run MCP server (STDIO transport)
mcp run src/server.py

# Run tests
python -m pytest tests/

# Inspect with MCP Inspector
npx @anthropic-ai/mcp-inspector
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

1. **Provider-agnostic LLM** — Gemini is default but easily swappable via dependency injection
2. **Lightweight Phase 1** — Only token utilization scoring; no heavy ML dependencies
3. **In-memory first** — SQLite persistence deferred to Phase 3
4. **FastMCP** — Uses the high-level `FastMCP` API for cleaner tool/resource registration
5. **Composite scoring** — Weighted formula allows tuning per-deployment
