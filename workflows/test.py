from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio


async def load_tools():
    servers = {
        "python_tools": {
            "transport": "stdio",
            "command": "uv",
            "args": [
                "run",
                "fastmcp",
                "run",
                "C:\\Users\\panka\\genai_project\\data_analysis_agent\\mcp_server\\main.py",
            ],
        }
    }

    client = MultiServerMCPClient(servers)
    tools = await client.get_tools()
    return tools


tools = asyncio.run(load_tools())
print([i.name for i in tools if i.name == "run_pandas_queries"])
