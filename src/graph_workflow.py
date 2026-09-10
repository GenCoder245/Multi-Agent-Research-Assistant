from langgraph.graph.state import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import MemorySaver

from src.nodes import query_router_node, query_enhancer_node, research_agent_node, research_tools_node, supervisor_node
from src.route_functions import route_after_query_router, route_after_research, route_from_supervisor
from src.schemas import State


def get_graph():
    builder = StateGraph(state_schema=State)

    # --------------------------------
    # Query understanding
    # --------------------------------

    builder.add_node("query_router", query_router_node)
    builder.add_node("query_enhancer", query_enhancer_node)
    
    # --------------------------------
    # Research Agent
    # --------------------------------

    builder.add_node("research_agent", research_agent_node)
    builder.add_node("research_tools", research_tools_node)

    # --------------------------------
    # Supervisor
    # --------------------------------

    # New Supervisor Agent node
    builder.add_node("supervisor", supervisor_node)

    # --------------------------------
    # START
    # --------------------------------

    # START → Router
    builder.add_edge(START, "query_router")

    # --------------------------------
    # Query Router
    # --------------------------------

    # Router → Enhancer OR Supervisor Agent
    # Router to Supervisor Agent directly or via Enhancer
    builder.add_conditional_edges("query_router",
                                route_after_query_router,
                                {
                                    "enhancer":  "query_enhancer",
                                    # "next": "research_agent"
                                    "next": "supervisor"
                                })

    # --------------------------------
    # Enhancer
    # --------------------------------

    # Enhancer → Supervisor Agent
    # builder.add_edge("query_enhancer","research_agent")
    builder.add_edge("query_enhancer","supervisor")


    # --------------------------------
    # Supervisor
    # --------------------------------

    # Supervisor → Research Agent or Finish
    builder.add_conditional_edges(
                "supervisor",
                route_from_supervisor,
                {
                    "research":"research_agent",
                    "finish":END,
                }
    )


    # --------------------------------
    # Research Agent
    # --------------------------------

    # Research Agent → Tool or Supervisor
    builder.add_conditional_edges(
        "research_agent",
        #tools_condition,
        route_after_research,
        {
            "tools": "research_tools",
            "supervisor": "supervisor",
        }
    )

    # --------------------------------
    # Tools
    # --------------------------------

    # Tool → Research Agent
    builder.add_edge("research_tools","research_agent")

    # Start Adding Memory checkpointer. For now, keeping an In-memory checkpointer.
    memory = MemorySaver()

    graph = builder.compile(checkpointer=memory)

    return graph



