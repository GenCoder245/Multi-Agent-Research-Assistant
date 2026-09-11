from src.graph_workflow import get_graph
from langchain_core.messages import HumanMessage, AIMessage


def run_chat_loop(graph, chat_thread_id):
    """
    Runs a continuous terminal chat loop using LangGraph's graph.invoke().
    Exits when the user types 'exit' or 'quit'.
    """
    print("\n🚀 LangGraph Chat Loop Started! Type 'exit' or 'quit' to end the session.\n")
    
    # Initialize state with a blank message history
    state = {"messages": [], 
                "enhanced_query": None,
                "needs_enhancement":False,
                "next_node":None,
                "supervisor_reasoning":None}

    config = {"configurable":{"thread_id":chat_thread_id}}

    while True:
        try:
            # 1. Get user input
            user_input = input("🤖 You: ").strip()
            
            # 2. Check for exit commands
            if user_input.lower() in ["exit", "quit"]:
                print("\n👋 Goodbye!")
                break
                
            if not user_input:
                continue

            # 3. Append the new user message to the state
            state["messages"].append( HumanMessage(content=user_input))

            # 4. Invoke the graph
            response = graph.invoke(state, config=config)

            print(f"Full response: ")
            print(response)

            # 5. Extract and print only the latest assistant response
            latest_response = response["messages"][-1]

            print("\n🤖 Assistant:")

            latest_resp_content = getattr(latest_response, "content")

            if isinstance(latest_resp_content, list):
                latest_message = latest_resp_content[0]['text']
                print(latest_message)
            else:
                print(f"The latest_response is of type: {type(latest_response)}")
                latest_response.pretty_print()

            print() # Add an extra newline for readability

            # 6. Update the local state for the next turn
            state = response

        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}\n")


if __name__ == "__main__":
    graph = get_graph()

    # For Demo purposes, using normal thread-id's
    chat_thread_id = "11"

    # Set it to True during initial Run alone to get the graph as mermaid png.
    save_graph : bool = False

    if save_graph:
        # 1. Retrieve the raw PNG bytes from LangGraph
        png_bytes = graph.get_graph().draw_mermaid_png()

        # 2. Write the bytes into a local file
        with open("4_graph_till_supervisor.png", "wb") as f:
            f.write(png_bytes)

    # Run the Chat loop
    run_chat_loop(graph=graph, chat_thread_id=chat_thread_id)



    
