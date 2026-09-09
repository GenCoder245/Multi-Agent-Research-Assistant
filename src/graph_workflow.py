from langgraph.graph.state import StateGraph, START, END

from src.nodes import llm_node
from src.schemas import State


def get_graph():
    builder = StateGraph(State)

    builder.add_node("llm_node",llm_node)
    builder.add_edge(START, "llm_node")
    builder.add_edge("llm_node", END)

    graph=builder.compile()

    return graph



