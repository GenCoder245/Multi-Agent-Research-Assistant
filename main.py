from langchain_core.messages import HumanMessage, AIMessage

from src.tools_mcp import setup_mcp_tools
import asyncio

from config import Settings, get_settings
from src.llm_models import get_language_model
import structlog
from custom_logger import configure_logging
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

agent_asst_settings: Settings = get_settings()

from src.graph_workflow import get_graph

logger = structlog.get_logger()

configure_logging(agent_asst_settings.log_level)

async def run_chat_loop(graph, chat_thread_id):
    """
    Runs a continuous terminal chat loop using LangGraph's graph.ainvoke().
    Exits when the user types 'exit' or 'quit'.
    """
    logger.info("\n🚀 LangGraph Chat Loop Started! Type 'exit' or 'quit' to end the session.\n")
    
    # Initialize state with a blank message history
    state = {"messages": [], 
                "enhanced_query": None,
                "needs_enhancement":False,
                "next_node":None,
                "supervisor_reasoning":None,
                "current_stage":None,
            }

    config = {"configurable":{"thread_id":chat_thread_id}}

    while True:
        try:
            # 1. Get user input
            user_input = input("🤖 You: ").strip()
            
            # 2. Check for exit commands
            if user_input.lower() in ["exit", "quit"]:
                logger.info("\n👋 Goodbye!")
                break
                
            if not user_input:
                continue

            # 3. Append the new user message to the state
            state["messages"].append( HumanMessage(content=user_input))

            # 4. Invoke the graph
            response = await graph.ainvoke(state, config=config)

            logger.info(f"Full response: ")
            logger.info(response)

            # 5. Extract and print only the latest assistant response
            latest_response = response["messages"][-1]

            logger.info("\n🤖 Assistant:")

            latest_resp_content = getattr(latest_response, "content")

            if isinstance(latest_resp_content, list):
                latest_message = latest_resp_content[0]['text']
                logger.info(latest_message)
            else:
                logger.info(f"The latest_response is of type: {type(latest_response)}")
                latest_response.pretty_print()

            logger.info() # Add an extra newline for readability

            # 6. Update the local state for the next turn
            state = response

        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}\n")


async def main():

    # For Demo purposes, using normal thread-id's
    chat_thread_id = "35"

    llm_model = get_language_model(llm_settings=agent_asst_settings)

    # mcp_client is for future purposes.
    mcp_client, mcp_tools = await setup_mcp_tools(logger=logger)

    async with AsyncSqliteSaver.from_conn_string(agent_asst_settings.sqlite_database_name) as checkpointer_memory:
        if mcp_tools:
            graph = get_graph(
                memory_checkpointer=checkpointer_memory,
                language_model=llm_model,
                mcp_tools_list=mcp_tools,
            )
        else:
            graph = get_graph(
                memory_checkpointer=checkpointer_memory,
                language_model=llm_model,
                mcp_tools_list=None,
            )

        # Set it to True during initial Run alone to get the graph as mermaid png.
        save_graph: bool = False

        if save_graph:
            png_bytes = graph.get_graph().draw_mermaid_png()

            with open("6_graph_till_summarizer.png", "wb") as f:
                f.write(png_bytes)

        await run_chat_loop(graph=graph, chat_thread_id=chat_thread_id)


if __name__ == "__main__":
    asyncio.run(main())



    
