from langchain_core.messages import SystemMessage, HumanMessage

from src.schemas import State, QueryRouting, SupervisorDecision
from src.llm_models import llm
from src.prompts import ROUTING_PROMPT, ENHANCER_PROMPT, RESEARCH_SYSTEM_PROMPT, SUPERVISOR_PROMPT, SUPERVISOR_HUMAN_FINAL_PROMPT
from src.tools import tools_list

from langgraph.prebuilt import ToolNode

router_llm = llm.with_structured_output(schema=QueryRouting,
                                        method = 'json_schema')

research_llm = llm.bind_tools(tools_list)

supervisor_llm = llm.with_structured_output(SupervisorDecision)


# Nodes defined below:

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


def research_agent_node(state: State):
    # query = state.get("enhanced_query") or state["messages"][-1].content
    query = state.get("enhanced_query")

    if query:
        
        messages = [
            SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
            *state["messages"][:-1], # Conversation history till last before message
            HumanMessage(content=query), # Instead of last message(non-enhanced query), use the enhanced query as the latest message
        ]
    else:
        messages = [
            SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
            *state["messages"], # Full Conversation history
        ]


    response = research_llm.invoke(messages)

    # The research agent returns an AIMessage with tool_calls if needed to call a tool
    # or
    # A Final AIMessage with the answer if no (further) tool calls are needed.

    return {
        "messages": [response]
    }




research_tools_node = ToolNode(tools=tools_list)




def supervisor_node(state: State):

    messages = state["messages"]

    query = state.get("enhanced_query")

    # Final Prompt sent as HumanMessage after Supervisor gets results from Research Agent
    # To avoid getting the "Gemini model doesn't support pre-filling" error.
    # Will get the error when the Final Message in messages list is an AIMessage.

    if query:
        response = supervisor_llm.invoke(
            [
                SystemMessage(content=SUPERVISOR_PROMPT),
                *messages[:-1], # Conversation history till last before message
                HumanMessage(content=query), # Instead of last message(non-enhanced query), use the enhanced query as the latest message
                # The final request turn must be a user message or a function response.
                HumanMessage(content=SUPERVISOR_HUMAN_FINAL_PROMPT)
            ]
        )
    else:
        response = supervisor_llm.invoke(
            [
                SystemMessage(content=SUPERVISOR_PROMPT),
                *messages,
                # The final request turn must be a user message or a function response.
                HumanMessage(content=SUPERVISOR_HUMAN_FINAL_PROMPT)
            ]
        )         

    return {
        "next_node": response.next,
        "supervisor_reasoning": response.reason
    }







