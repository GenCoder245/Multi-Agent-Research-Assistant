from langchain_tavily import TavilySearch

from config import get_settings
settings = get_settings()
tavily_search = TavilySearch(
    max_results=3,
    topic="general",
    tavily_api_key=settings.tavily_api_key_value,
)

tools_list = [tavily_search]