from pydantic import Field, BaseModel
from typing import List, Optional, Literal
import pandas as pd
from dotenv import load_dotenv
import os
from typing import TypedDict, Annotated
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_core.messages import (
    SystemMessage,
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.output_parsers import PydanticOutputParser
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
import warnings
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
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


model_for_schema_generator = ChatOllama(model="gemma4:31b-cloud").bind_tools(tools)

model_for_schema_formatter = ChatOllama(model="gemma4:31b-cloud").bind_tools(tools)


class schema_for_subgraph_schema_generator(TypedDict):
    csv_schema: str
    messages: Annotated[List[BaseMessage], add_messages]


class schema_for_schema_formatter(BaseModel):
    schema_: str



parser_for_schema_formatter = PydanticOutputParser(
    pydantic_object=schema_for_schema_formatter
)

sys_prompt_for_schema_generator = f"""
You are a data schema generator. Your job is to analyze CSV files and produce clear, concise schema documentation that downstream teams can immediately understand and use.

## Your Task
Explore the CSV file thoroughly using `run_pandas_queries` tool and generate a natural-language schema document. Never guess—derive everything from actual data inspection.


## Execution Rules
- Use `run_pandas_queries` as many times as needed to fully understand each column
- Extract actual statistics: describe(), value_counts(), isnull().sum(), dtypes, head(), info() etc
- Be concise but specific enough that a colleague LLm can see the file without seeing it
- If the file cannot be read, explain the error and stop
- Return only the schema document—no preamble or additional commentary
"""

sys_prompt_for_schema_formatter = f"user will give you the output of an ai assistant your task is to covert it into following Output format - {parser_for_schema_formatter.get_format_instructions()}"


def schema_generator(state: schema_for_subgraph_schema_generator):
    pr = [SystemMessage(content=sys_prompt_for_schema_generator), *state["messages"]]
    res = model_for_schema_generator.invoke(pr)

    return {"messages": [res]}


def schema_formatter(state: schema_for_subgraph_schema_generator):
    pr = [
        SystemMessage(content=sys_prompt_for_schema_formatter),
        HumanMessage(content=state["messages"][-1].content),
    ]
    res = model_for_schema_formatter.invoke(pr)
    res = parser_for_schema_formatter.invoke(res.content)

    return {"csv_schema": res.schema_}


def tool_call_condition(
    state: schema_for_subgraph_schema_generator,
) -> Literal["tools", "schema_formatter"]:
    if state["messages"][-1].tool_calls:
        return "tools"
    return "schema_formatter"


graph = StateGraph(schema_for_subgraph_schema_generator)

graph.add_node("schema_generator", schema_generator)
graph.add_node("schema_formatter", schema_formatter)
graph.add_node("tools", ToolNode(tools=tools))

graph.add_edge(START, "schema_generator")
graph.add_conditional_edges("schema_generator", tool_call_condition)

graph.add_edge("tools", "schema_generator")
graph.add_edge("schema_formatter", END)

schema_generator_workflow = graph.compile()


async def run_schema_generator_workflow(content):
    res = await schema_generator_workflow.ainvoke(
        {"messages": [HumanMessage(content=content)]}
    )
    return res


if __name__ == "__main__":
    res = asyncio.run(
        run_schema_generator_workflow(
            content="File path = C:\\Users\\panka\\genai_project\\data_analysis_agent\\data\\Iris.csv"
        )
    )
    print(res["csv_schema"])
