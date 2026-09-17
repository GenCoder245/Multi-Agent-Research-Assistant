import json
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from pydantic import BaseModel, Field

from config import get_settings
from custom_logger import configure_logging
from src.graph_workflow import get_graph
from src.llm_models import get_language_model
from src.tools_mcp import setup_mcp_tools


logger = structlog.get_logger()

STAGES = {
    "query_router": "Understanding your question",
    "query_enhancer": "Clarifying conversation context",
    "supervisor": "Planning the research workflow",
    "research_agent": "Researching the topic",
    "research_tools": "Searching reliable sources",
    "analysis_agent": "Analysing the findings",
    "summary_agent": "Preparing the final answer",
}


class ChatRequest(BaseModel):
    query: str = Field(min_length=1)
    session_id: str = Field(default="default", min_length=1)


def _sse(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=True)}\n\n"


def _message_text(message: Any) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in content
        )
    return str(content) if content else ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    llm = get_language_model(llm_settings=settings)
    mcp_client, mcp_tools = await setup_mcp_tools(logger=logger)

    async with AsyncSqliteSaver.from_conn_string(settings.sqlite_database_name) as checkpointer:
        if mcp_tools:
            app.state.graph = get_graph(
                memory_checkpointer=checkpointer,
                language_model=llm,
                mcp_tools_list=mcp_tools,
            )
            app.state.mcp_client = mcp_client
            yield
        else:
            app.state.graph = get_graph(
                            memory_checkpointer=checkpointer,
                            language_model=llm,
                            mcp_tools_list=None,
                        )
            app.state.mcp_client = None
            yield

app = FastAPI(
    title="Multi-Agent Technical Research Assistant API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _chat_events(request: ChatRequest) -> AsyncIterator[str]:
    graph = getattr(app.state, "graph", None)
    if graph is None:
        yield _sse({"type": "error", "error": "The workflow is not ready."})
        return

    config = {"configurable": {"thread_id": request.session_id}}
    input_state = {
        "messages": [HumanMessage(content=request.query)],
        "enhanced_query": None,
        "needs_enhancement": False,
        "next_node": None,
        "supervisor_reasoning": None,
        "current_stage": None,
    }
    answer_emitted = False
    try:
        yield _sse({"type": "stage", "stage": STAGES["query_router"], "node": "query_router", "initial": True})
        async for event in graph.astream(
            input_state,
            config=config,
            stream_mode=["messages", "updates"],
            version="v2",
        ):  
            # print(f"--->>> Event: {event}")
            event_type = event.get("type") if isinstance(event, dict) else None

            if event_type == "messages":
                message, metadata = event.get("data", (None, {}))
                node = metadata.get("langgraph_node") if isinstance(metadata, dict) else None
                if node in STAGES:
                    yield _sse({"type": "stage", "stage": STAGES[node], "node": node, "event_type":event_type})
                if node == "summary_agent":
                    delta = _message_text(message)
                    if delta:
                        answer_emitted = True
                        yield _sse({"type": "chunk", "delta": delta, "chunk_event_type":event_type})
                continue

            if event_type == "updates":
                updates = event.get("data", {})
                if not isinstance(updates, dict):
                    continue
                for node, update in updates.items():
                    if node not in STAGES:
                        continue
                    yield _sse({"type": "stage", "stage": STAGES[node], "node": node, "event_type":event_type})
                    if node == "summary_agent" and not answer_emitted:
                        messages = update.get("messages", []) if isinstance(update, dict) else []
                        if messages:
                            answer = _message_text(messages[-1])
                            if answer:
                                answer_emitted = True
                                yield _sse({"type": "chunk", "delta": answer, "chunk_event_type":event_type})

        yield _sse({"type": "done", "done": True})
    except Exception as exc:
        logger.exception("Chat workflow failed", error=str(exc))
        yield _sse({"type": "error", "error": str(exc)})


@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="`query` parameter is not provided for POST /chat")
    return StreamingResponse(
        _chat_events(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint used by Docker and orchestration tools."""
    return {"status": "ok", "service": "multi-agent-research-assistant"}


@app.get("/graph_image")
async def graph_image() -> Response:
    graph = getattr(app.state, "graph", None)
    if graph is None:
        raise HTTPException(status_code=503, detail="The workflow is not ready.")
    return Response(content=graph.get_graph().draw_mermaid_png(), media_type="image/png")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=True)