from src.graph_workflow import get_graph
from langchain_core.messages import HumanMessage, AIMessage


if __name__ == "__main__":
    graph = get_graph()

    input_query = "Explain AI Agents briefly."
    # input_query = "Explain it in more detail."

    response = graph.invoke(
    {
        "messages": [
            HumanMessage(content=input_query)
        ],
        "enhanced_query": None,
        "needs_enhancement":False
    }
)
    # 1) For the input_query "Explain AI Agents briefly.", the output is:

    # Query passed downstream: Explain AI Agents briefly. 
    # ------------------------------------------------------------------------------------------------------------------------------------------------------
    # Full Response: {'messages': [HumanMessage(content='Explain AI Agents briefly.', additional_kwargs={}, response_metadata={}, id='74483udfu-9738-0aew-a7c1-93893ne992093')], 'enhanced_query': None, 'needs_enhancement': False}

    # No enhancement was needed, so the same input query was passed downstream as-is.



    # 2) For the input_query "Explain it in more detail.", the output is:

    # Query passed downstream: Explain the previous topic in more detail.
    # ------------------------------------------------------------------------------------------------------------------------------------------------------
    # Full Response: {'messages': [HumanMessage(content='Explain it in more detail.', additional_kwargs={}, response_metadata={}, id='74483udfu-9738-0aew-a7c1-93893ne992094')], 'enhanced_query': 'Explain the previous topic in more detail.', 'needs_enhancement': True}

    # Enhancement was needed, so the input query was enhanced to "Explain the previous topic in more detail." and passed downstream.
    # NOTE: Since it doesn't have full convo history yet, it was just enhanced to explain previous topic instead of actually mentioning the specific topic.

    print("-"*150)
    print(f"Full Response: {response}")

    
