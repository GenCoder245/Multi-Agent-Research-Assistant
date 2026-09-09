from langgraph.graph.state import StateGraph, START, END

from src.nodes import query_router_node, query_enhancer_node, next_node
from src.route_functions import route_after_query_router
from src.schemas import State


def get_graph():
    builder = StateGraph(state_schema=State)

    builder.add_node("query_router", query_router_node)
    builder.add_node("query_enhancer", query_enhancer_node)
    builder.add_node("next_node",next_node)

    builder.add_edge(START, "query_router")

    builder.add_conditional_edges("query_router",
                                route_after_query_router,
                                {
                                    "enhancer":  "query_enhancer",
                                    "next": "next_node"
                                })

    builder.add_edge("query_enhancer","next_node")

    builder.add_edge("next_node", END)


    graph = builder.compile()

    return graph



