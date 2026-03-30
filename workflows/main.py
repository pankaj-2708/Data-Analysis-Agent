from workflows.tools import run_graph_queries,run_pandas_queries
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
from pydantic import Field,BaseModel
from typing import List,Optional,Literal
from dotenv import load_dotenv
import os
load_dotenv()
os.environ['LANGSMITH_PROJECT']='data-analysis-agent-testing'

model_for_query_generator=ChatNVIDIA(model="mistralai/mistral-small-4-119b-2603",max_completion_tokens=10000)


class schema_for_pandas_query_generator(BaseModel):
    queries_description:List[str]=Field(...,description='list of queries description')
    
parser_for_pandas_query_generator=PydanticOutputParser(pydantic_object=schema_for_pandas_query_generator)

class schema_for_graph_query_generator_util(BaseModel):
    queries_description:str=Field(...,description='querie description')
    image_name:str=Field(...,description='Name of the file for chart/graph should be a png file')
    
class schema_for_graph_query_generator(BaseModel):
    queries_description:List[schema_for_graph_query_generator_util]
    
parser_for_graph_query_generator=PydanticOutputParser(pydantic_object=schema_for_graph_query_generator)

class schema_for_main_graph(TypedDict):
    file_path:str
    pandas_queries:List[schema_for_pandas_query_generator]
    graph_queries:List[schema_for_graph_query_generator]
    pandas_results:List[str]
    csv_schema=str
    
    
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





def graph_query_generator(state:schema_for_main_graph):
    pr=[SystemMessage(content=sys_prompt_for_graph_query_generator),HumanMessage(content=f'Csv description - {state["csv_schema"]}')]

    res=model_for_query_generator.invoke(pr)
    res=parser_for_graph_query_generator.invoke(res.content)

    return {'graph_queries':res}
    

def pandas_query_generator(state:schema_for_main_graph):
    pr=[SystemMessage(content=sys_prompt_for_pandas_query_generator),HumanMessage(content=f'Csv description - {state["csv_schema"]}')]

    res=model_for_query_generator.invoke(pr)
    res=parser_for_pandas_query_generator.invoke(res.content)

    return {'pandas_queries':res}
    
    
    
    