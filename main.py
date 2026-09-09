from src.graph_workflow import get_graph
from langchain_core.messages import HumanMessage, AIMessage


if __name__ == "__main__":
    graph = get_graph()

    input_query = "Explain AI Agents briefly."

    response = graph.invoke({"messages":[
        HumanMessage(content=input_query)
    ]})

    print("-"*150)
    print(f"Full Response: {response}")

    # Full Response: {'messages': [HumanMessage(content='Explain AI Agents briefly.', additional_kwargs={}, response_metadata={}, id='dfwijo-83u3jdhe-3389kjcs'), 
    # AIMessage(content=[{'type': 'text', 'text': '**AI Agents** are artificial intelligence programs designed to **perceive** their environment, **make decisions**, and **take actions** autonomously to achieve a specific goal. \n\nUnlike traditional software that only follows strict, pre-written rules, or standard chatbots that just answer questions, AI agents can reason, plan, and use tools to get work done.\n\n### Key Components of an AI Agent:\n1. **Perception:** Taking in data (text, images, sensor data, or user prompts).\n2. **Reasoning/Brain:** Using an LLM (Large Language Model) or algorithm to plan the steps needed to reach the goal.\n3. **Action:** Executing tasks (e.g., writing code, searching the web, sending an email, or moving a robotic arm).\n4. **Memory:** Remembering past interactions and results to learn and adjust its strategy.\n\n### Real-World Example:\nInstead of you having to search for flights, compare prices, and book a ticket yourself, you could tell an **AI travel agent**: *"Book me a weekend trip to Chicago under $300."* The agent will autonomously browse the web, make choices, and complete the booking for you.', 
    # 'extras': {'signature': 'jfiewr389r2398ud230932eCjzAGbD7EkKFefTHvUKWmqlDsUmUTqQOH/qIx9aaUSvZfe89ru94u3h49u9udj3j938'}}], additional_kwargs={}, 
    # response_metadata={'finish_reason': 'STOP', 'model_name': 'gemini-3.5-flash-lite', 'safety_ratings': [], 'model_provider': 'google_genai'}, 
    # id='lc_run--003iiedji-8n3c-7d12-2637j-11c1538738huhu-0', tool_calls=[], invalid_tool_calls=[], 
    # usage_metadata={'input_tokens': 6, 'output_tokens': 250, 'total_tokens': 256, 'input_token_details': {'cache_read': 0}})]}
            


    if isinstance(response['messages'][-1], AIMessage):
        print("-"*150)
        print(f"The response is an AIMessage class.")

        # response['messages'][-1].content[0]['text'] - This is how to extract text response for Gemini 3.x models
        print("*"*150)
        print(f"The actual response: {response['messages'][-1].content[0]['text']}")
        
    else:
        print("-"*150)
        print(f"The response is not an AIMessage class. It is of type: {type(response['messages'])}")


    
