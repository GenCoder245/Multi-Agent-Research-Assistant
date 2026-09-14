from typing import Annotated, List, TypedDict, Literal
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from pydantic import BaseModel, Field

class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

    # Added during query enhancement.
    enhanced_query: str | None
    needs_enhancement: bool

    # Added during supervisor agent decision-making.
    next_node : str | None
    supervisor_reasoning: str | None


class QueryRouting(BaseModel):
    needs_enhancement: bool = Field(
        description="Whether the user query requires conversation context "
                    "to become self-contained."
    )


class SupervisorDecision(BaseModel):
    next: Literal["research","analysis","finish"] = Field(description="The next step in the workflow.")
    reason: str = Field("The reason why supervisor thinks the specified node should be invoked next.")