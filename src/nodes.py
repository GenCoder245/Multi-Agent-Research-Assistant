from src.schemas import State
from src.llm_models import llm


def llm_node(state:State):
    response = llm.invoke(state["messages"])

    return {"messages":[response]}