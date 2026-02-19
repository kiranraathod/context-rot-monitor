
# Agentic Context Rot Monitor

**The "Check Engine Light" for your AI Agent's Context Window.**

[![MCP](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

An **MCP Server** that monitors, scores, and remediates **context degradation** ("context rot") in LLM agent systems. It detects when your agent is losing focus, getting clogged with duplicates, or hitting the "Lost-in-the-Middle" danger zone.

## Features

*   **Context Health Score (CHS)**: Real-time 0-100 score of your context quality.
*   **Rot Detection**: Uses embeddings to detect **Topic Drift** and **Redundancy**.
*   **Active Remediation**: Tools to **Recommend Pruning** and **Summarize** context.
*   **Alerts**: Auto-triggers warnings when health drops or redundancy spikes.
*   **History**: Tracks health trends over time in a local SQLite database.

## Installation

### Prerequisites
*   Python 3.10+
*   `uv` (recommended) or `pip`

### Install as MCP Server

**Option 1: Using `uv` (Recommended)**
```bash
# Clone the repo
git clone https://github.com/kiranraathod/context-rot-monitor.git
cd context-rot-monitor

# Install dependencies (including Phase 2+ features)
uv pip install -e ".[phase2]"
```

## Configuration

Set the following environment variables if you want to use Remediation features (Summarization):

```bash
export GOOGLE_API_KEY="your-gemini-api-key"
```

## Usage

### 1. Run with `stdio` (Default)
Ideal for **Gemini CLI**, **Claude Desktop**, or **Cursor**.

```bash
uv run python -m src.server
```

### 2. Run with `sse` (HTTP)
Ideal for remote hosting or debugging with **MCP Inspector**.

```bash
uv run python -m src.server --transport sse --port 8000
```

## Tools & Resources

**Tools**:
*   `get_token_metrics(context)`: Basic usage stats.
*   `analyze_context_health(context, goal)`: Full health check (Score, Status, Drill-down).
*   `detect_context_rot(context, goal)`: Deep-dive report on redundancy/drift.
*   `recommend_pruning(context)`: Returns indices of junk chunks to cut.
*   `summarize_context(context)`: LLM-powered compression.

**Resources**:
*   `rot://health/current`: Real-time health state.
*   `rot://alerts/active`: Active warnings list.
*   `rot://metrics/history`: Historical trend data (JSON).

## Architecture

Built with:
*   **mcp** (FastMCP)
*   **tiktoken** (Token counting)
*   **sentence-transformers** (Embeddings/Relevance)
*   **google-genai** (LLM Summarization)
*   **sqlite3** (History persistence)

## License
MIT