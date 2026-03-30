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
from pydantic import Field, BaseModel
from typing import List, Optional, Literal
from dotenv import load_dotenv
from graph_query_executor import workflow_for_graph_query
from pandas_query_executor import workflow_for_pandas_query,schema_for_pandas_query_formatter
from schema_generator import schema_generator_workflow
import os
import operator
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.types import Send
from IPython.display import Markdown,display
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


load_dotenv()
os.environ["LANGSMITH_PROJECT"] = "data-analysis-agent-testing"

model_for_markdown_generator=ChatNVIDIA(model="mistralai/mistral-small-4-119b-2603",max_completion_tokens=10000)
model_for_query_generator = ChatNVIDIA(
    model="mistralai/mistral-small-4-119b-2603", max_completion_tokens=10000
)


class schema_for_pandas_query_generator(BaseModel):
    queries_description: List[str] = Field(
        ..., description="list of queries description"
    )


parser_for_pandas_query_generator = PydanticOutputParser(
    pydantic_object=schema_for_pandas_query_generator
)


class schema_for_graph_query_generator_util(BaseModel):
    queries_description: str = Field(..., description="querie description")
    image_name: str = Field(
        ..., description="Name of the file for chart/graph should be a png file"
    )


class schema_for_graph_query_generator(BaseModel):
    queries_description: List[schema_for_graph_query_generator_util]


parser_for_graph_query_generator = PydanticOutputParser(
    pydantic_object=schema_for_graph_query_generator
)


class schema_for_main_graph(TypedDict):
    file_path:str
    pandas_queries:List[schema_for_pandas_query_generator]
    graph_queries:List[schema_for_graph_query_generator]
    pandas_results:Annotated[List[schema_for_pandas_query_formatter],operator.add]
    csv_schema:str
    markdown:str


sys_prompt_for_pandas_query_generator = f"""
You are a senior data analyst specializing in statistical analysis using Python and pandas.

The user will provide a description of a CSV file. Your task is to generate descriptions of all pandas queries required to produce a comprehensive statistical analysis report of the data.

STRICT RULES:
1. Generate ONLY statistical queries — descriptive stats, distributions, correlations, aggregations, value counts, missing value analysis, outlier detection, and group-by summaries.
2. Use ONLY pandas (and numpy where necessary). No matplotlib, seaborn, plotly, or any visualization libraries.
3. Do NOT write actual code. Write clear, precise natural-language DESCRIPTIONS of each query.
4. These query descriptions will be consumed by another LLM in the next step to write the actual pandas code — so be explicit and unambiguous. Each description must be self-contained and implementation-ready.
5. Every description must specify: the operation type, the column(s) involved, and the expected output shape/format.

Output format:
{parser_for_pandas_query_generator.get_format_instructions()}
"""

sys_prompt_for_graph_query_generator = f"""
You are a senior data analyst and data visualization expert specializing in exploratory data analysis (EDA).

The user will provide a description of a CSV file. Your task is to generate descriptions of all charts and graphs required to produce a comprehensive, visually rich data analysis report.

STRICT RULES:
1. Generate ONLY visualization queries — distribution plots, correlation heatmaps, bar charts, line charts, scatter plots, box plots, pair plots, pie charts, time series plots, etc.
2. Use ONLY plotly (plotly.express or plotly.graph_objects). Do NOT include any statistical computations or pandas aggregation logic.
3. Do NOT write actual code. Write clear, precise natural-language DESCRIPTIONS of each chart.
4. These chart descriptions will be consumed by another LLM in the next step to write the actual plotly code — so be explicit and unambiguous. Each description must be self-contained and implementation-ready.
5. Every description must specify:
   - Chart type and the preferred plotly module (px vs go) — e.g., "plotly.express scatter", "plotly.graph_objects Heatmap"
   - Column(s) involved (x-axis, y-axis, color/grouping if any)
   - The analytical insight this chart is meant to reveal
   - Any grouping, filtering, or sorting that should be applied before plotting

Output format:
{parser_for_graph_query_generator.get_format_instructions()}
"""


def graph_query_generator(state: schema_for_main_graph):
    pr = [
        SystemMessage(content=sys_prompt_for_graph_query_generator),
        HumanMessage(content=f'Csv description - {state["csv_schema"]}'),
    ]

    res = model_for_query_generator.invoke(pr)
    res = parser_for_graph_query_generator.invoke(res.content)

    return {"graph_queries": res}


def pandas_query_generator(state: schema_for_main_graph):
    pr = [
        SystemMessage(content=sys_prompt_for_pandas_query_generator),
        HumanMessage(content=f'Csv description - {state["csv_schema"]}'),
    ]

    res = model_for_query_generator.invoke(pr)
    res = parser_for_pandas_query_generator.invoke(res.content)

    return {"pandas_queries": res}

async def wrapper_for_schema_generator(state:schema_for_main_graph):
    res=await schema_generator_workflow.ainvoke({'messages':[HumanMessage(content=f'File path = {state["file_path"]}')]})
    # print(res['csv_schema'])
    return {'csv_schema':res['csv_schema']}

async def wrapper_for_pandas_query_executor(inp):
    query=inp['query']
    csv_schema=inp['csv_schema']

    messages=HumanMessage(content=f"csv_schema: {csv_schema} \n\n task:{query}")
    
    res=await workflow_for_pandas_query.ainvoke({'messages':[messages],'query':query})
    return {'pandas_results':[res['formatted_result']]}



def fanout_for_pandas_query(state:schema_for_main_graph):
    res=[]
    for pd_q in state['pandas_queries']:
        res.append(Send('wrapper_for_pandas_query_executor',{'csv_schema':state['csv_schema'],'query':pd_q}))
    return res


async def wrapper_for_graph_query_executor(inp):
    task=inp['task']
    file_path=inp['file_path']
    csv_schema=inp['csv_schema']

    messages=HumanMessage(content=f"""
        task-{task}
        file_path-{f"./data/{file_path}"}
        csv_schema-{csv_schema}
""")
    
    res=await workflow_for_graph_query.ainvoke({'messages':[messages]})
    return 


def fanout_for_graph_query(state:schema_for_main_graph):
    res=[]
    for pd_q in state['graph_queries'].queries_description:
        res.append(Send('wrapper_for_graph_query_executor',{'csv_schema':state['csv_schema'],'task':pd_q.queries_description,'file_path':pd_q.image_name}))
    return res


def dummy_collector(state:schema_for_main_graph):
    return


class schema_for_markdown_generator(BaseModel):
    markdown:str=Field(...,description="markdown file")

parser_for_markdown_generator=PydanticOutputParser(pydantic_object=schema_for_markdown_generator)

sys_prompt_for_markdown_generator = f"""
You are a Markdown report generator. The user will provide you with:
- A CSV schema
- Pandas queries and their outputs
- Plotly graph queries and the file paths of the saved chart images

Your task is to produce a beautiful, well-structured, and informative Markdown analysis report of the CSV file.

Follow these guidelines when generating the report:
- Begin with a title and a brief overview of the dataset
- Organise the report into clear sections (e.g., Dataset Overview, Key Statistics, Visual Insights)
- Present query outputs as clean Markdown tables wherever applicable
- Embed saved chart images using the exact provided file paths — do not alter or substitute any part of the path
- Add concise, meaningful commentary under each section to interpret the data and charts
- Use headers, dividers, and formatting to ensure the report is easy to read and visually polished

Output format- 
{parser_for_markdown_generator.get_format_instructions()}
"""

def markdown_generator(state:schema_for_main_graph):
    po=""
    for i in state['pandas_results']:
        po=po+f'query= {i.query}'+f"\n result= {i.result}\n\n"
        
    gq=""
    for i in state['graph_queries'].queries_description:
        gq=gq+'\n'+i.queries_description+'\n'+f'File path = ./data/{i.image_name}'+'\n'
    pr=f"""
    Csv schema - 
    {state['csv_schema']}



    Pandas queries and output - 
    {po}

    
    graph queries and output - 
    {gq}
    """

    # print(pr)
    pr=[SystemMessage(content=sys_prompt_for_markdown_generator),HumanMessage(content=pr)]
    res=model_for_markdown_generator.invoke(pr)
    res=parser_for_markdown_generator.invoke(res)

    
    with open('markdown.md','w') as f:
        f.write(res.markdown)
        
    return {'markdown':res.markdown}


graph=StateGraph(schema_for_main_graph)

graph.add_node('wrapper_for_schema_generator',wrapper_for_schema_generator)
graph.add_node('pandas_query_generator',pandas_query_generator)
graph.add_node('graph_query_generator',graph_query_generator)
graph.add_node('wrapper_for_pandas_query_executor',wrapper_for_pandas_query_executor)
graph.add_node('wrapper_for_graph_query_executor',wrapper_for_graph_query_executor)
graph.add_node('dummy_collector',dummy_collector)
graph.add_node('markdown_generator',markdown_generator)
# graph.add_node('tools',ToolNode(tools=[run_pandas_queries,run_graph_queries]))

graph.add_edge(START,'wrapper_for_schema_generator')
graph.add_edge('wrapper_for_schema_generator','pandas_query_generator')
graph.add_edge('wrapper_for_schema_generator','graph_query_generator')

graph.add_conditional_edges('pandas_query_generator',fanout_for_pandas_query,['wrapper_for_pandas_query_executor'])
graph.add_conditional_edges('graph_query_generator',fanout_for_graph_query,['wrapper_for_graph_query_executor'])

graph.add_edge('wrapper_for_graph_query_executor','dummy_collector')
graph.add_edge('wrapper_for_pandas_query_executor','dummy_collector')
graph.add_edge('dummy_collector','markdown_generator')
graph.add_edge('markdown_generator',END)

check_ptr=InMemorySaver()
workflow=graph.compile(checkpointer=check_ptr)

async def run_workflow():
    config={'configurable': {'thread_id': '1'}}
    r=await workflow.ainvoke({'file_path':'C:\\Users\\panka\\genai_project\\data_analysis_agent\\data\\Iris.csv'},config=config)
    return r

if __name__=="__main__":
    res=asyncio.run(run_workflow())
    display(Markdown(res['markdown']))