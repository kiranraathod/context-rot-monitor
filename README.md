
# Agentic Context Rot Monitor

MCP Server for monitoring, scoring, and remediating context degradation in LLM agent systems.

## Features

- **Real-time Context Health Score**: Tracks utilization, relevance, redundancy, and coherence.
- **Token Metrics**: Detailed breakdown of token usage and limits.
- **Rot Detection**: Alerts when context quality degrades below thresholds.

## Installation

1. Clone the repository:
   ```bash
   git clone <repo_url>
   cd context-rot-monitor
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   # Using uv (recommended)
   uv venv
   uv pip install -r pyproject.toml
   ```

## Usage

### Running the Server

To run the MCP server:

```bash
# Using standard MCP CLI
mcp run src/server.py
```

### Tools

- `get_token_metrics(context_text, max_window_size)`: Returns token counts and utilization.
- `analyze_context_health(context_text, step_number)`: Computes a composite health score (0-100).

### Resources

- `rot://health/current`: JSON resource providing the latest health score and status.

## Development

Run tests:
```bash
python -m unittest discover tests
```