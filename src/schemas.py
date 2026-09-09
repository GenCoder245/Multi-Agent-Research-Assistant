from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from pydantic import BaseModel, Field

class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    
    enhanced_query: str | None
    needs_enhancement: bool


class QueryRouting(BaseModel):
    needs_enhancement: bool = Field(
        description="Whether the user query requires conversation context "
                    "to become self-contained."
    )
