from pydantic import Field, BaseModel
from typing import Literal
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langchain_core.messages import (
    SystemMessage,
    BaseMessage,
    HumanMessage,
)
from langchain_core.output_parsers import PydanticOutputParser
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
import warnings

warnings.filterwarnings("ignore")
load_dotenv()


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
tools = [i for i in tools if i.name == "run_pandas_queries"]

model_for_query_executor = ChatNVIDIA(
    model="mistralai/mistral-small-4-119b-2603", max_completion_tokens=10000
).bind_tools(tools)


class schema_for_pandas_query_formatter(BaseModel):
    query: str = Field(..., description="query")
    result: str = Field(..., description="result")


parser_for_pandas_query_formatter = PydanticOutputParser(
    pydantic_object=schema_for_pandas_query_formatter
)


class schema_for_pandas_query_executor(TypedDict):
    messages: Annotated[BaseMessage, add_messages]
    query: str
    formatted_result: schema_for_pandas_query_formatter


sys_prompt_for_pandas_query_executor = """
You are a data analyst specializing in pandas. Your task is to:

1. Analyze the CSV schema and user requirements
2. Write efficient, readable pandas queries to solve the problem
3. Execute the queries and return the results

Guidelines:
- Write clean, well-commented code
- Use appropriate pandas methods (groupby, merge, filter, etc.)
- Handle edge cases and missing data gracefully
- Explain your approach before executing


Note-
Use full file path for loading the csv file.
"""


def chat_node_for_pandas_query_executor(state: schema_for_pandas_query_executor):
    pr = [
        SystemMessage(content=sys_prompt_for_pandas_query_executor),
        *state["messages"],
    ]
    res = model_for_query_executor.invoke(pr)

    return {"messages": [res]}


sys_prompt_for_pandas_query_formatter = f"""
You are a data formatting specialist. Your task is to:

1. Receive a user query and an AI-generated answer
2. Format the answer according to the specified output format
3. Ensure all required fields are populated correctly
4. Validate the formatted output for consistency

Output Format Requirements:
{parser_for_pandas_query_formatter.get_format_instructions()}
"""


def pandas_query_formator(state: schema_for_pandas_query_executor):
    pr = [
        SystemMessage(content=sys_prompt_for_pandas_query_formatter),
        HumanMessage(content=f"""
    query - {state['query']} 
    result - {state['messages'][-1].content}
    """),
    ]

    res = model_for_query_executor.invoke(pr)
    res = parser_for_pandas_query_formatter.invoke(res.content)
    return {"formatted_result": res}


def tool_call_condition(
    state: schema_for_pandas_query_executor,
) -> Literal["tools", "schema_formatter"]:
    if state["messages"][-1].tool_calls:
        return "tools"
    return "schema_formatter"


graph = StateGraph(schema_for_pandas_query_executor)

graph.add_node("chat_node", chat_node_for_pandas_query_executor)
graph.add_node("schema_formatter", pandas_query_formator)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tool_call_condition)
graph.add_edge("tools", "chat_node")

workflow_for_pandas_query = graph.compile()
