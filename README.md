# Multi-Agent Technical Research Assistant

A Multi-Agent Technical research assistant built with LangGraph, FastAPI, Streamlit, and Google Gemini. The application routes a question through specialized agents, searches external sources with Tavily, analyzes the findings, summarizes them and streams the final response back to the user.

## Features

- Multi-Agent LangGraph orchestration workflow with routing, query enhancement, supervision, research, analysis, and summary agents.
- Tavily search through the Tavily MCP server.
- Streaming responses over Server-Sent Events (SSE).
- Conversation-specific LangGraph checkpoints stored in SQLite.
- Streamlit chat interface with live workflow stages, multi-turn conversation and a workflow graph view.
- FastAPI health endpoint for Docker and orchestration readiness checks.

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- API credentials for Google Gemini and Tavily
- Docker Desktop and Docker Compose for containerized execution

## Architecuture:

The full architecure is present in "Multi-agent-architecture.png" file

## Configuration

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your-gemini-api-key
TAVILY_API_KEY=your-tavily-api-key

# Optional OpenAI and LangSmith settings
OPENAI_API_KEY=
OPENAI_CHAT_MODEL=
LANGSMITH_TRACING=false
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=multi-agent-research-assistant

SQLITE_DATABASE_NAME=checkpoints.sqlite
```

Settings are loaded by `config.py`. Do not commit `.env` or API keys to source control.


## Install with uv

```powershell
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

## Run locally

Start the backend in one terminal:

```powershell
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --reload
```

Start the frontend in a second terminal:

```powershell
streamlit run streamlit_app.py
```

Open <http://localhost:8501>. The API is available at <http://localhost:8000>, with Swagger documentation at <http://localhost:8000/docs>.

If the API is hosted elsewhere, set the frontend URL before starting Streamlit:

```powershell
$env:API_BASE="http://localhost:8000"
streamlit run streamlit_app.py
```

## Run with Docker Compose

Make sure `.env` exists, then build and start both services:

```powershell
docker compose up --build
```

Open <http://localhost:8501>. The backend is available at <http://localhost:8000>.

The frontend depends on the backend health check and starts only after `GET /health` returns HTTP 200. The health check begins after the FastAPI lifespan has initialized the LLM, MCP tools, and LangGraph workflow. SQLite checkpoints are stored in the named `checkpoints` volume.

Stop the services:

```powershell
docker compose down
```

Remove the stored conversation checkpoints as well:

```powershell
docker compose down -v
```

## API

### `POST /chat`

Request body:

```json
{
	"query": "How does AI agents work?",
	"session_id": "conversation-1"
}
```

The response is an SSE stream containing workflow stage events, answer chunks, and a final completion event.

### `GET /health`

Returns the service readiness status and is used by Docker Compose.

### `GET /graph_image`

Returns a PNG rendering of the LangGraph workflow.

## Project structure

```text
fastapi_app.py       FastAPI endpoints and SSE response handling
streamlit_app.py     Streamlit user interface
src/                 LangGraph workflow, agents, models, prompts, and tools
config.py            Environment-backed application settings
Dockerfile.backend   Backend image definition
Dockerfile.frontend  Frontend image definition
docker-compose.yml   Health-gated multi-container setup
```

## Common Troubleshooting

- If the backend exits during startup, check that `GEMINI_API_KEY` and `TAVILY_API_KEY` are present in `.env`.
- Check backend logs with `docker compose logs -f backend`.
- Check frontend logs with `docker compose logs -f frontend`.
- If the frontend cannot connect locally, verify that `API_BASE` points to the API URL and that port `8000` is available.