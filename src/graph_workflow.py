from langgraph.graph.state import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import MemorySaver

from src.nodes import query_router_node, query_enhancer_node, research_agent_node, research_tools_node
from src.route_functions import route_after_query_router
from src.schemas import State


def get_graph():
    builder = StateGraph(state_schema=State)

    builder.add_node("query_router", query_router_node)
    builder.add_node("query_enhancer", query_enhancer_node)
    
    # New research nodes
    builder.add_node("research_agent", research_agent_node)
    builder.add_node("research_tools", research_tools_node)

    # START → Router
    builder.add_edge(START, "query_router")

    # Router → Enhancer OR Research Agent
    # Router to Research Agent directly or via Enhancer
    builder.add_conditional_edges("query_router",
                                route_after_query_router,
                                {
                                    "enhancer":  "query_enhancer",
                                    "next": "research_agent"
                                })

    # Enhancer → Research Agent
    builder.add_edge("query_enhancer","research_agent")

    # Research Agent → Tool OR END
    builder.add_conditional_edges(
        "research_agent",
        tools_condition,
        {
            "tools": "research_tools",
            END: END,
        }
    )

    # Tool → Research Agent
    builder.add_edge("research_tools","research_agent")

    # Start Adding Memory checkpointer. For now, keeping an In-memory checkpointer.
    memory = MemorySaver()

    graph = builder.compile(checkpointer=memory)

    return graph



