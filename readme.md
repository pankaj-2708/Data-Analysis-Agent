# Data Analysis Agent

An agentic pipeline that takes a CSV file, analyzes it end-to-end, and produces a structured Markdown report with charts — fully automated using LangGraph and MCP tools,.

---

## Workflow

<!-- Replace the line below with your workflow diagram -->
<img src='./images/workflow.png'>

---

## How It Works

1. **Schema Generation** — The agent reads the uploaded CSV and generates a detailed natural-language schema by running pandas introspection queries via an MCP tool server.
2. **Query Planning** — Two parallel planners generate:
   - A list of pandas analysis queries (statistics, correlations, anomalies, etc.)
   - A list of chart/graph descriptions with assigned filenames
3. **Parallel Execution** — Both query sets are fanned out in batches and executed concurrently:
   - Pandas queries run through `workflow_for_pandas_query` and return structured results
   - Graph queries run through `workflow_for_graph_query`, generating and saving PNG charts
4. **Report Generation** — All results are consolidated into a polished Markdown report with embedded chart images.

---

## Project Structure

```
├── workflows/
│   ├── main.py                  # Orchestrator graph (LangGraph)
│   ├── schema_generator.py      # CSV schema extraction subgraph
│   ├── pandas_query_executor.py # Pandas analysis subgraph
│   └── graph_query_executor.py  # Matplotlib chart generation subgraph
├── mcp_server/
│   └── main.py                  # FastMCP server exposing Python execution tools
└── webapp/
    └── frontend.py              # Streamlit UI
```

---

## Tech Stack

| Component | Library / Service |
|---|---|
| Orchestration | LangGraph |
| Tool Execution | FastMCP (stdio transport) |
| LLM ↔ MCP Bridge | `langchain-mcp-adapters` |
| Data Analysis | pandas |
| Charting | Matplotlib |
| Persistence | SQLite (`AsyncSqliteSaver`) |
| Frontend | Streamlit |

---

## Setup

### Prerequisites

- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv) (used to run the MCP server)

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment

Create a `.env` file in the project root:

```env
LANGSMITH_API_KEY=your_key_here   # optional, for tracing
other api keys for respective llm
```


### Run the app

```bash
streamlit run webapp/frontend.py
```

Upload a CSV file and click **Run Analysis Agent**. The report renders in the UI once the pipeline completes.

---

## MCP Tools

The MCP server exposes two execution tools:

| Tool | Description |
|---|---|
| `run_pandas_queries` | Executes multi-line pandas code via `exec()` and returns named variables |
| `run_graph_queries` | Executes a Matplotlib script and saves the output chart as PNG |

Both tools run with a configurable timeout (default: 10s).

---

## Output

- **Markdown report** saved to `data/markdown.md`
- **PNG charts** saved to the `data/` folder
- Report is rendered directly in the Streamlit UI after the run completes

---

*Created by Pankaj Maulekhi*