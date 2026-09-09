from langchain_tavily import TavilySearch # Inherits from BaseTool

tavily_search = TavilySearch(max_results=3, topic="general")

tools_list = [tavily_search]