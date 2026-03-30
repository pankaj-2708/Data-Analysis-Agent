from pydantic import Field,BaseModel
from typing import List,Optional,Literal
import pandas as pd
from dotenv import load_dotenv
import os
from typing import TypedDict,Annotated
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_core.messages import SystemMessage,BaseMessage,HumanMessage,ToolMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.tools import tool
from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from tools import run_pandas_queries


load_dotenv()

model_for_schema_generator=ChatNVIDIA(model="mistralai/mistral-small-4-119b-2603",max_completion_tokens=10000).bind_tools([run_pandas_queries])
model_for_schema_formatter=ChatNVIDIA(model="mistralai/mistral-small-4-119b-2603",max_completion_tokens=10000)


class schema_for_subgraph_schema_generator(TypedDict):
    csv_schema:str
    messages:Annotated[List[BaseMessage],add_messages]
    
class schema_for_schema_formatter(BaseModel):
    schema_:str

class schema_for_schema_formatter(BaseModel):
    schema_:str

parser_for_schema_formatter=PydanticOutputParser(pydantic_object=schema_for_schema_formatter)

sys_prompt_for_schema_generator = f"""
You are a data analysis assistant specialized in generating detailed schemas for CSV files.
The schema you produce will be used by downstream pipeline nodes to reference, query, and validate the file.

## Your Task
The user will provide a CSV file path. Use the `run_pandas_queries` tool to thoroughly explore
the file and generate a comprehensive schema based on what you observe — never guess or assume.

## What to Capture
Explore the file sufficiently to document the following:

### File-Level Metadata
- total rows, total columns, duplicate row count

### Per-Column Details
For every column in the file, document:
- **Column name**: exact name as it appears in the file
- **Data type**: pandas dtype (e.g., int64, float64, object, datetime64)
- **Semantic type**: what the column likely represents (e.g., identifier, timestamp, categorical, numeric metric)
- **Sample values**: 3–5 representative values
- **Null count & percentage**: how much data is missing
- **Unique value count**: number of distinct values
- **Range or categories**: min/max for numeric columns; top categories for object columns
- **Description**: Description about data

## Rules
- Run as many `run_pandas_queries` calls as needed — do not stop until all columns are fully documented.
- Always derive every value from tool output — never fabricate or estimate.
- If the file cannot be read, report the error in the schema's error field and stop.
- Do not include any commentary outside the required output format.
"""




sys_prompt_for_schema_formatter=f"user will give you the output of an ai assistant your task is to covert it into following Output format - {parser_for_schema_formatter.get_format_instructions()}"



def schema_generator(state:schema_for_subgraph_schema_generator):
    
    pr=[SystemMessage(content=sys_prompt_for_schema_generator),*state['messages']]
    res=model_for_schema_generator.invoke(pr)
    
    return {"messages":[res]}


def schema_formatter(state:schema_for_subgraph_schema_generator):
    pr=[SystemMessage(content=sys_prompt_for_schema_formatter),HumanMessage(content=state['messages'][-1].content)]
    res=model_for_schema_formatter.invoke(pr)
    res=parser_for_schema_formatter.invoke(res.content)

    return {'csv_schema':res.schema_}


def tool_call_condition(state:schema_for_subgraph_schema_generator)->Literal['tools','schema_formatter']:
    if state['messages'][-1].tool_calls:
        return 'tools'
    return 'schema_formatter'


graph=StateGraph(schema_for_subgraph_schema_generator)

graph.add_node('schema_generator',schema_generator)
graph.add_node('schema_formatter',schema_formatter)
graph.add_node('tools',ToolNode(tools=[run_pandas_queries]))

graph.add_edge(START,'schema_generator')
graph.add_conditional_edges('schema_generator',tool_call_condition)

graph.add_edge('tools','schema_generator')
graph.add_edge('schema_formatter',END)

check_ptr=InMemorySaver()
workflow=graph.compile(checkpointer=check_ptr)

if __name__=="__main__":
    config={"configurable":{'thread_id':'2'}}
    res=workflow.invoke({'messages':[HumanMessage(content='File path = ./data/Iris.csv')]},config=config)
    print(res['csv_schema'])