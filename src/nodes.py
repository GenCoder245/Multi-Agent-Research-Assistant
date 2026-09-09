from langchain_core.messages import SystemMessage

from src.schemas import State, QueryRouting
from src.llm_models import llm
from src.prompts import ROUTING_PROMPT, ENHANCER_PROMPT


router_llm = llm.with_structured_output(schema=QueryRouting,
                                        method = 'json_schema')

def query_router_node(state:State):

    messages = state['messages']

    response = router_llm.invoke(
                        [
                            SystemMessage(content=ROUTING_PROMPT),
                            *messages
                        ] 
                    )

    return {
        "needs_enhancement": response.needs_enhancement
    }




def query_enhancer_node(state:State):
    messages = state["messages"]

    enhancer_response = llm.invoke([
        SystemMessage(content=ENHANCER_PROMPT),
        *messages
    ])


    # The enhancer does not modify - state["messages"] because
    # The conversation history remains the actual conversation.
    # The enhanced query is an internal interpretation.

    return {
        "enhanced_query": enhancer_response.content[0]['text']
    }



# Just a dummy node for now
def next_node(state:State):
    query = state.get("enhanced_query") or state['messages'][0].content

    print(f"Query passed downstream: {query}")

    return {}







