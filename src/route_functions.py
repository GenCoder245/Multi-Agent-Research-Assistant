from src.schemas import State

def route_after_query_router(state: State):
    if state["needs_enhancement"]:
        return "enhancer"

    return "next"


# Added new custom router for tools_condition
def route_after_research(state: State):
    last_message = state["messages"][-1]

    tool_callings = last_message.tool_calls
    if tool_callings and len(tool_callings) > 0:
        return "tools"

    return "supervisor"



def route_from_supervisor(state: State):
    if state["next_node"] == "research":
        return "research"

    if state["next_node"] == "analysis":
            return "analysis"

    return "finish"






