# 🧠 Agentic Context Rot Monitor — Project Handover

> **MCP Server for monitoring, scoring, and remediating context degradation in LLM agent systems.**

---

## Project Summary

| Field | Detail |
|-------|--------|
| **Project** | Agentic Context Rot Monitor |
| **Type** | MCP (Model Context Protocol) Server |
| **Language** | Python |
| **Status** | Pre-development — Architecture finalized |
| **Date** | February 16, 2026 |
| **Origin** | Extended from the [Context-Engineering-for-Multi-Agent-Systems](https://github.com/Denis2054/Context-Engineering-for-Multi-Agent-Systems) book (Packt, Denis Rothman) |

---

## Problem Statement

**Context rot** is the insidious degradation of LLM agent performance as context accumulates during multi-step execution. Unlike out-of-memory crashes, context rot is *silent* — the agent keeps running but produces progressively worse output.

### Root Causes

| Cause | Impact |
|-------|--------|
| **Positional Bias** | LLMs recall start/end of context better than middle ("Lost-in-the-Middle") |
| **Attention Dilution** | Attention budget thins as tokens grow; critical details get missed |
| **Context Pollution** | Irrelevant/redundant data drowns out signal |
| **Reasoning Decay** | Complex reasoning degrades with longer inputs, even with correct retrieval |
| **Signal-to-Noise Collapse** | Low SNR → hallucinations and off-topic drift |

### Market Gap

> [!IMPORTANT]
> As of Feb 2026, **no MCP server exists for context rot monitoring**. Existing tools (LangSmith, DeepEval, OpenTelemetry) are either not MCP-native or lack context-rot-specific metrics. This is a greenfield opportunity.

---

## Architecture

### MCP Server Design

```
┌─────────────────────┐     ┌──────────────┐     ┌─────────────────────────────┐
│ MCP Host             │     │ MCP Client    │     │ Context Rot Monitor Server  │
│ (Claude, VS Code,    │────▶│ (JSON-RPC 2.0)│────▶│                             │
│  Cursor, etc.)       │     │               │     │  Tools:    6 analysis tools  │
│                      │     │ STDIO or HTTP │     │  Resources: 4 data feeds    │
└─────────────────────┘     └──────────────┘     │  Prompts:  2 templates       │
                                                  └─────────────────────────────┘
```

### MCP Primitives

#### 🔧 Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `analyze_context_health` | Compute composite health score | `context_text`, `step_number`, `model_name` |
| `detect_context_rot` | Multi-signal rot detection on execution trace | `execution_trace`, `threshold` |
| `get_token_metrics` | Token counts, utilization %, growth rate | `context_text`, `max_window_size` |
| `score_relevance_decay` | Embedding-based relevance drift from original goal | `context_chunks[]`, `original_goal` |
| `recommend_pruning` | Suggest context segments to remove/summarize | `context_text`, `goal`, `keep_ratio` |
| `summarize_context` | LLM-powered context compression | `context_text`, `target_token_count` |

#### 📊 Resources

| URI | Description |
|-----|-------------|
| `rot://health/current` | Real-time Context Health Score (0–100) |
| `rot://metrics/history` | Time-series metrics for analysis |
| `rot://alerts/active` | Currently triggered alerts |
| `rot://config` | Server configuration & thresholds |

#### 📝 Prompts

| Name | Purpose |
|------|---------|
| `diagnose_rot` | Template for diagnosing context degradation causes |
| `optimize_context` | Template for suggesting optimization strategies |

---

## Core Metric: Context Health Score (CHS)

```
CHS = w₁·(1 - utilization_ratio) + w₂·relevance_score + w₃·(1 - redundancy_ratio) + w₄·coherence_score
```

| Signal | Measurement | ⚠️ Warn | 🔴 Critical |
|--------|-------------|---------|-------------|
| Token Utilization | `current_tokens / max_window` | > 80% | > 90% |
| Growth Rate | Δ tokens per step | > 2× avg | > 4× avg |
| Relevance Decay | Cosine similarity vs. original goal | < 0.5 | < 0.3 |
| Redundancy Ratio | Duplicate content detection | > 30% | > 50% |
| Positional Risk | Critical info in middle 40% zone | Detected | High density |
| Coherence | Semantic consistency across chunks | Declining | Contradictory |

---

## Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **MCP SDK** | `mcp` (official Python SDK) | Best supported; built-in STDIO + HTTP transports |
| **LLM** | Google Gemini (provider-agnostic design) | Familiar; easy to swap for OpenAI/Anthropic |
| **Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) | Lightweight, local, real-time relevance scoring |
| **Token Counting** | `tiktoken` | Battle-tested (already in Context Engine codebase) |
| **Vector Similarity** | NumPy cosine similarity | No external DB needed for pairwise comparisons |
| **Storage** | SQLite (local) / in-memory | Simple persistence, zero dependencies |
| **Transport** | STDIO (IDE) + Streamable HTTP (remote) | Covers local dev and production deployment |

---

## Project Structure

```
context-rot-monitor/
├── src/
│   ├── server.py                  # MCP server entry point & registration
│   ├── tools/
│   │   ├── analyze.py             # analyze_context_health, detect_context_rot
│   │   ├── metrics.py             # get_token_metrics
│   │   ├── relevance.py           # score_relevance_decay (embedding-based)
│   │   └── remediate.py           # recommend_pruning, summarize_context
│   ├── resources/
│   │   ├── health.py              # rot://health/current
│   │   ├── history.py             # rot://metrics/history
│   │   └── alerts.py              # rot://alerts/active
│   ├── prompts/
│   │   ├── diagnose.py            # diagnose_rot template
│   │   └── optimize.py            # optimize_context template
│   ├── core/
│   │   ├── scorer.py              # Context Health Score algorithm
│   │   ├── detector.py            # Rot pattern detection engine
│   │   └── tokenizer.py           # Token counting utilities
│   └── storage/
│       └── metrics_store.py       # SQLite/in-memory persistence
├── tests/
│   ├── test_scorer.py
│   ├── test_detector.py
│   └── test_tools.py
├── pyproject.toml
├── mcp.json                       # MCP server manifest
└── README.md
```

---

## Development Roadmap

### Phase 1: Core Monitoring (Week 1–2)
- [ ] Bootstrap Python MCP server with STDIO transport
- [ ] Implement `get_token_metrics` tool
- [ ] Implement `analyze_context_health` tool
- [ ] Build basic Context Health Score (token utilization + growth rate)
- [ ] Create `rot://health/current` resource
- [ ] Write unit tests for scorer and tokenizer

### Phase 2: Rot Detection (Week 2–3)
- [ ] Integrate `sentence-transformers` for embedding-based relevance scoring
- [ ] Implement `score_relevance_decay` tool
- [ ] Add redundancy detection (near-duplicate content finder)
- [ ] Build positional risk analysis
- [ ] Implement `detect_context_rot` tool (multi-signal analysis)
- [ ] Create `rot://alerts/active` resource

### Phase 3: Remediation (Week 3–4)
- [ ] Implement `recommend_pruning` tool
- [ ] Implement `summarize_context` tool (LLM-powered compression)
- [ ] Build configurable alert threshold system
- [ ] Create `diagnose_rot` and `optimize_context` prompt templates
- [ ] Create `rot://metrics/history` resource

### Phase 4: Production Polish (Week 4+)
- [ ] Add Streamable HTTP transport
- [ ] Publish to MCP registry
- [ ] Publish to PyPI
- [ ] Write comprehensive README with usage examples
- [ ] Record demo video for portfolio

---

## Context from Source Codebase

This project extends patterns from the **Context-Engineering-for-Multi-Agent-Systems** book repo. Key files to understand:

| File | What to Study |
|------|---------------|
| [engine.py](file:///c:/Users/ratho/Desktop/data%20analysis/clone_github/Context-Engineering-for-Multi-Agent-Systems/commons/engine.py) | `ExecutionTrace` class — existing trace logging; `context_engine()` Plan→Execute loop |
| [helpers.py](file:///c:/Users/ratho/Desktop/data%20analysis/clone_github/Context-Engineering-for-Multi-Agent-Systems/commons/helpers.py) | `count_tokens()`, `create_mcp_message()` — patterns to build on |
| [registry.py](file:///c:/Users/ratho/Desktop/data%20analysis/clone_github/Context-Engineering-for-Multi-Agent-Systems/commons/registry.py) | `AgentRegistry` — how tools/capabilities are described for the Planner |
| [agents.py](file:///c:/Users/ratho/Desktop/data%20analysis/clone_github/Context-Engineering-for-Multi-Agent-Systems/commons/agents.py) | Librarian/Researcher/Writer agents — context accumulation pattern |
| [engine/engine.py](file:///c:/Users/ratho/Desktop/data%20analysis/clone_github/Context-Engineering-for-Multi-Agent-Systems/commons/engine/engine.py) | Enhanced version with `tokens_in`/`tokens_out` tracking per step |

### Key Patterns to Carry Forward

1. **MCP Message Envelope** — `{protocol_version, sender, content, metadata}`
2. **Dependency Injection** — No global state; pass `client`, `model`, `index` as params
3. **`$$STEP_N_OUTPUT$$` Chaining** — This is where context rot accumulates; monitor this
4. **Token Analytics** — The enhanced engine already counts tokens; extend this into rot scoring

---

## Key References

| Resource | Link |
|----------|------|
| MCP Spec | [modelcontextprotocol.io](https://modelcontextprotocol.io/docs/concepts/architecture) |
| MCP Python SDK | [github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) |
| MCP Inspector | [github.com/modelcontextprotocol/inspector](https://github.com/modelcontextprotocol/inspector) |
| Context Rot (Redis) | [redis.io/blog/context-rot-ai-agents](https://redis.io/blog/context-rot-ai-agents/) |
| Lost-in-the-Middle | [arxiv.org/abs/2307.03172](https://arxiv.org/abs/2307.03172) |
| Anthropic Context Engineering | [anthropic.com/engineering/context-engineering](https://www.anthropic.com/engineering/context-engineering) |
