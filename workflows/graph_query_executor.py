import pandas as pd
from dotenv import load_dotenv
import os
from typing import TypedDict, Annotated
from langchain_core.messages import (
    SystemMessage,
    BaseMessage,
)
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
import warnings

warnings.filterwarnings("ignore")
load_dotenv()
from langchain_ollama import ChatOllama


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
tools = [i for i in tools if i.name == "run_graph_queries"]


model_for_graph_query_executor = model = ChatOllama(model="qwen2.5-coder:3b").bind_tools(tools)


class schema_for_graph_query_executor(TypedDict):
    messages: Annotated[BaseMessage, add_messages]


sys_prompt_for_graph_query_executor = """
You are a data analyst. The user will provide you a task, a CSV schema, csv file path, and an image file path.

Your task is to write a multiline Python script for Matplotlib to:
- Generate a chart or graph for the given task
- Use the csv file path for reading the CSV
- Save the figure at EXACTLY the provided image file path — do not modify, append, or substitute any part of it
- Use the given tools to execute the script

CRITICAL RULES — YOU MUST FOLLOW THESE WITHOUT EXCEPTION:
- NEVER call plt.show() under any circumstances — not even commented out
- NEVER use fig.show() or any display/render method
- ALWAYS use plt.savefig("<exact_image_file_path>") to save the figure
- ALWAYS call plt.close() after saving to free memory
- Use full file paths for both saving the image and loading the CSV

"""


def chat_node_for_graph_query_executor(state: schema_for_graph_query_executor):
    pr = [
        SystemMessage(content=sys_prompt_for_graph_query_executor),
        *state["messages"],
    ]
    res = model_for_graph_query_executor.invoke(pr)

    return {"messages": [res]}


graph = StateGraph(schema_for_graph_query_executor)

graph.add_node("chat_node", chat_node_for_graph_query_executor)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

workflow_for_graph_query = graph.compile()
