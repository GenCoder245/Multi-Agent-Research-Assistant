from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage

from src.schemas import State, QueryRouting, SupervisorDecision
from src.prompts import ROUTING_PROMPT, ENHANCER_PROMPT, RESEARCH_SYSTEM_PROMPT, SUPERVISOR_PROMPT
from src.prompts import SUPERVISOR_HUMAN_FINAL_PROMPT, ANALYSER_PROMPT, SUMMARY_AGENT_PROMPT
from src.tools import tools_list

from langgraph.prebuilt import ToolNode

llm = None
router_llm = None
supervisor_llm = None
research_llm = None


def _conversation_without_tool_calls(messages):
    """Keep conversational text while removing tool protocol messages."""
    conversation = []

    for message in messages:
        if isinstance(message, ToolMessage):
            continue

        if isinstance(message, AIMessage) and message.tool_calls:
            if message.content:
                conversation.append(AIMessage(content=message.content))
            continue

        conversation.append(message)

    return conversation

# To set the LLM Model for the graph nodes to use
def set_language_model(language_model):
    global llm, router_llm, supervisor_llm, research_llm

    llm = language_model
    router_llm = llm.with_structured_output(
        schema=QueryRouting,
        method="json_schema",
    )
    supervisor_llm = llm.with_structured_output(SupervisorDecision)

    # If MCP tools list is available, it will later be binded
    research_llm = llm.bind_tools(tools_list)    

def initialize_mcp_tools(mcp_tools_list):
    global research_llm, llm
    
    research_llm = llm.bind_tools(mcp_tools_list)
    research_tools_node_mcp = ToolNode(tools=mcp_tools_list)
    return research_tools_node_mcp


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
        "needs_enhancement": response.needs_enhancement,
        "enhanced_query": None,
        "next": None,
    }




def query_enhancer_node(state:State):

    # print(f"Enhancer: The messages before: {state['messages']}")
    messages = _conversation_without_tool_calls(state["messages"])

    # print(f"Enhancer: The messages after: {messages}")
    enhancer_response = llm.invoke([
        SystemMessage(content=ENHANCER_PROMPT),
        *messages
    ])


    # The enhancer does not modify - state["messages"] because
    # The conversation history remains the actual conversation.
    # The enhanced query is an internal interpretation.

    #print('<->'*100)
    #print(f"Enhancer: The response: {enhancer_response}")
    #print('<->'*100)
    
    content = enhancer_response.content
    if isinstance(content, list):
        content = "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict)
        )

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Query enhancer returned no text response.")

    return {"enhanced_query": content.strip()}


def supervisor_node(state: State):

    state_messages = state["messages"]

    query = state.get("enhanced_query")

    if state.get("current_stage"):
        SUPERVISOR_PROMPT_FINAL = SUPERVISOR_PROMPT.format(current_stage = state.get("current_stage"))
    else:
        SUPERVISOR_PROMPT_FINAL = SUPERVISOR_PROMPT.format(current_stage = "Not in sub-agents stage yet")

    if query:
        if isinstance(state_messages[-1], HumanMessage):
            #print("="*120)
            #print("Supervisor: Last message is a HumanMessage.")
            #print(f"Supervisor: HumanMessage content: {state_messages[-1]}")
            #print("="*120)
            
            response = supervisor_llm.invoke(
                [
                    SystemMessage(content=SUPERVISOR_PROMPT_FINAL),
                    *state_messages[:-1], # Conversation history till last before message
                    HumanMessage(content=query), # Instead of last message(non-enhanced query), use the enhanced query as the latest message
                    # The final request turn must be a user message or a function response to avoid getting the "Gemini model doesn't support pre-filling" error..
                    # Will get that error when the Final Message in messages list is an AIMessage.
                    HumanMessage(content=SUPERVISOR_HUMAN_FINAL_PROMPT)
                ]
            )
        else:

            #print("="*120)
            #print(f"Supervisor: Last message is {type(state_messages[-1])}. ")
            #print(f"Supervisor: {type(state_messages[-1])} content: {state_messages[-1]}")
            #print("="*120)
             
            response = supervisor_llm.invoke(
                        [
                            SystemMessage(content=SUPERVISOR_PROMPT_FINAL),
                            *state_messages,
                            HumanMessage(content=query), # Instead of last message(non-enhanced query), use the enhanced query as the latest message
                            # The final request turn must be a user message or a function response.
                            HumanMessage(content=SUPERVISOR_HUMAN_FINAL_PROMPT)
                        ]
                    )
    else:
        #print("="*120)
        #print("Supervisor: Using Full convo history....")
        #print(f"Supervisor: Full convo last message content: {state_messages[-1]}")
        #print("="*120)
         
        response = supervisor_llm.invoke(
            [
                SystemMessage(content=SUPERVISOR_PROMPT_FINAL),
                *state_messages,
                # The final request turn must be a user message or a function response.
                HumanMessage(content=SUPERVISOR_HUMAN_FINAL_PROMPT)
            ]
        )         

    return {
        "next_node": response.next,
        "supervisor_reasoning": response.reason
    }


def research_agent_node(state: State):
    # query = state.get("enhanced_query") or state["messages"][-1].content
    query = state.get("enhanced_query")
    state_messages = state['messages']

    if query:
        # If the last message in the state is a ToolMessage, we should include it in the messages list for context.
        if isinstance(state_messages[-1], ToolMessage):

            #print("*"*100)
            #print("Researcher: Last message is a ToolMessage. Including it in the research agent's context.")
            #print(f"Researcher: ToolMessage content: {state_messages[-1]}")
            #print("*"*100)

            messages = [
                        SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
                        *state_messages,
                        HumanMessage(content=query), # Using the enhanced query as the latest message
                    ]
            
        elif isinstance(state_messages[-1], AIMessage):

            #print("*"*100)
            #print(f"Researcher: Last message is a AIMessage. Including it in the research agent's context.")
            #print(f"Researcher: AIMessage latest content: {state_messages[-1]}")
            #print("*"*100)

            messages = [
                        SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
                        *state_messages, # Conversation history till last before message
                        HumanMessage(content=query), # Instead of last message(non-enhanced query), use the enhanced query as the latest message
                    ]
            
        elif isinstance(state_messages[-1], HumanMessage): # For HumanMessage, we can replace the last message with the enhanced query.:
            #print("*"*100)
            #print(f"Researcher: Last message is a HumanMessage. Including it in the research agent's context.")
            #print(f"Researcher HumanMessage latestcontent: {state_messages[-1]}")
            #print("*"*100)

            messages = [
                        SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
                        *state_messages[:-1], # Conversation history till last before message
                        HumanMessage(content=query), # Instead of last message(non-enhanced query), use the enhanced query as the latest message
                    ]

    else:
        #print("*"*100)
        #print("Researcher: Using Full convo history....")
        #print(f"Researcher: Full convo last message content: {state_messages[-1]}")
        #print("*"*100)

        messages = [
            SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
            *state_messages, # Full Conversation history
        ]


    response = research_llm.invoke(messages)

    # The research agent returns an AIMessage with tool_calls if needed to call a tool
    # or
    # A Final AIMessage with the answer if no (further) tool calls are needed.

    response.name = "Researcher_node"
    
    if response.tool_calls:
        response.name = "Researcher_node_with_tools"
        
        return {
            "messages": [response]
        }

    return {
        "messages": [response],
        "current_stage": "research"
    }


research_tools_node = ToolNode(tools=tools_list)


def analysis_agent_node(state: State):

    messages = [
        SystemMessage(content=ANALYSER_PROMPT),
        *state["messages"],
        HumanMessage(
            content="""
            Analyze the research findings produced so far.
            """
        )
    ]

    response = llm.invoke(messages)

    response.name = "Analyser_node"
    return {
        "messages": [response],
        "current_stage": "analysis"
    }



def summary_agent_node(state: State):

    messages = [
        SystemMessage(content=SUMMARY_AGENT_PROMPT),
        *state["messages"],
        HumanMessage(
            content="""
            Using the research and analysis completed so far,
            produce the final answer to the user's original question.
            """
        )
    ]

    response = llm.invoke(messages)

    response.name = "Summarizer_node"
    return {
        "messages": [response],
        "current_stage": "summary"
    }










