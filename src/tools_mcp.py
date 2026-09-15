import os
from langchain_mcp_adapters.client import MultiServerMCPClient

search_tool = None

async def setup_mcp_tools():
    client = MultiServerMCPClient({
            "tavily": {
                "url": "https://mcp.tavily.com/mcp/",
                "transport": "streamable_http",
                "headers": {"Authorization": f"Bearer {os.environ['TAVILY_API_KEY']}"},
            }
        })

    tools_mcp = await client.get_tools()

    # print(f"MCP Tools available are: {tools_mcp}")
    print(f"Total {len(tools_mcp)} MCP tools and their names: {[tool.name for tool in tools_mcp]}")


    search_tool = [tool for tool in tools_mcp if tool.name == 'tavily_search']

    return client, search_tool