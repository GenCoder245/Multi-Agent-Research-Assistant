from src.schemas import State

def route_after_query_router(state: State):
    if state["needs_enhancement"]:
        return "enhancer"

    return "next"