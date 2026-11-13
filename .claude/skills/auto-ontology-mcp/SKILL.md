---
name: auto-ontology-mcp
description: "Query an NVIDIA Auto Ontology deployment's semantic layer in natural language. Use when a task needs to know what a business term means according to the data team, or asks a data question that must resolve through a glossary rather than raw SQL. Not for local SQLite/CSV work."
---

# Auto Ontology (NVIDIA)

A Python framework — Apache-2.0, public beta — for building a **semantic, graph-based
reasoning layer over data**. It sits between an LLM and the warehouse so that
"active customer" means one reviewed thing instead of a fresh guess per query. It gives
deterministic query generation, better context retrieval, and explainable answers.

This folder vendors the pieces an agent needs to *use* such a deployment, not the
deployment itself.

```
SKILL.md                 this file
README.md                mcp/ — how the MCP server installs and what it exposes
MCP.md                   docs/mcp.md — full tool list, config vars, architecture
auto-ontology-api.json   the OpenAPI spec the MCP server builds itself from
pyproject.toml           the MCP package (4 deps: fastmcp, httpx, pydantic, python-dotenv)
LICENSE                  Apache-2.0
```

## Running it

The MCP server is a plain HTTP client of an Auto-Ontology deployment: **it holds no
database credentials and no credentials of its own** — the deployment signs each caller
in, so a session can do exactly what the person behind it can.

```bash
uvx --from "git+https://github.com/NVIDIA/auto-ontology.git#subdirectory=mcp" \
    auto-ontology-mcp
# needs one thing: where the deployment is
export AUTO_ONTOLOGY_API_URL=https://auto-ontology.example.com
```

Client config (Cursor / Claude Desktop) is just the URL — no secrets:

```json
{ "mcpServers": { "auto-ontology": { "url": "https://auto-ontology-mcp.example/mcp" } } }
```

Tools: `ask_question` (text-to-SQL through the glossary — returns the answer, the SQL, and
the rows), plus `search_terms`, `describe_table`, `check_answerable` and friends for
learning the vocabulary first. **Every tool reads.** Nothing modifies the glossary, the
catalog, or the databases.

## Verified here

The MCP package was installed locally in a Python 3.11 venv and the server boots:

```
Starting Auto Ontology MCP server — version 1.2.0, listening on http://localhost:3003
Server: auto-ontology, 1.2.0   (FastMCP 3.4.11)
build_server(settings) -> tuple[FastMCP, httpx.AsyncClient]
```

It needs an actual deployment to answer anything, which does not exist here.

## The honest caveat

**The full server does not run in this environment, and probably not in yours.**
`auto-ontology-server` requires Python **3.12–3.13** and pulls ~450 packages plus a git
dependency (`apache-ossie-nvidia-auto-ontology` from a git URL). This sandbox has Python
3.11, no Postgres, no Docker. The MCP client is the practical 10%; the other 90% is a
Docker Compose stack with Postgres, a FastAPI backend and a Next.js frontend.

So: installed as reference and as a runnable MCP client against a deployment you host,
not as a local data layer. There is no MIKAY data to put in an ontology yet — when the
episode catalogue, upload queue and QA results get real, this is the thing that would
make them queryable without an agent guessing at column names.
