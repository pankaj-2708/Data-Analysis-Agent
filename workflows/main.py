from typing import TypedDict, Annotated
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)
from langchain_core.output_parsers import PydanticOutputParser
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from pydantic import Field, BaseModel
from typing import List
from dotenv import load_dotenv
from graph_query_executor import workflow_for_graph_query
from pandas_query_executor import (
    workflow_for_pandas_query,
    schema_for_pandas_query_formatter,
)
from schema_generator import schema_generator_workflow
import os
import operator
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.types import Send
from IPython.display import Markdown, display
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.memory import InMemorySaver
import warnings
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite

warnings.filterwarnings("ignore")


load_dotenv()

image_folder = "C:/Users/panka/genai_project/data_analysis_agent/data"


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

model_for_markdown_generator = ChatNVIDIA(
    model="mistralai/mistral-small-4-119b-2603", max_completion_tokens=10000
)
model_for_query_generator = ChatNVIDIA(model="mistralai/mistral-small-4-119b-2603", max_completion_tokens=10000)


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
        ..., description="Name of the file for chart/graph it should be a png file "
    )


class schema_for_graph_query_generator(BaseModel):
    queries_description: List[schema_for_graph_query_generator_util]


parser_for_graph_query_generator = PydanticOutputParser(
    pydantic_object=schema_for_graph_query_generator
)


class schema_for_main_graph(TypedDict):
    file_path: str
    pandas_queries: List[schema_for_pandas_query_generator]
    graph_queries: List[schema_for_graph_query_generator]
    pandas_results: Annotated[List[schema_for_pandas_query_formatter], operator.add]
    csv_schema: str
    markdown: str


sys_prompt_for_pandas_query_generator = f"""
You are a senior data analyst specializing in exploratory data analysis using Python and pandas.

The user will provide a CSV file description and schema. Your task is to generate comprehensive descriptions of ALL pandas queries needed to deeply understand the data—from basic summaries to advanced statistical insights.

## Your Goal
Create a complete set of queries that progressively reveal patterns, anomalies, relationships, and insights in the data. Think like an analyst uncovering every dimension of the dataset.
Generate 5-10 queries

## Query Categories (Generate Queries Across ALL Categories)

### 1. Basic Data Understanding (Simple Queries)
- Row and column counts, data types, memory usage
- First/last few rows to see data structure
- Null value counts and percentages per column
- Duplicate row analysis
- Data type validation and conversions needed

### 2. Univariate Analysis (Simple to Moderate)
- Descriptive statistics: mean, median, std, min, max, quartiles
- Distribution analysis: value_counts() for categorical columns, histogram-style analysis for numeric
- Skewness and kurtosis for numeric columns
- Top/bottom N values for each column
- Cardinality analysis (unique value counts)

### 3. Data Quality & Anomalies (Moderate)
- Missing data patterns: which rows have the most nulls, which columns correlate with nulls
- Outlier detection: IQR method, z-score analysis per numeric column
- Inconsistent or unexpected values (e.g., negative ages, future dates)
- String anomalies: extra whitespace, case inconsistencies, special characters
- Duplicate detection: full row duplicates and key-based duplicates

### 4. Relationships & Patterns (Moderate to Complex)
- Correlation matrix: numeric-to-numeric relationships
- Categorical associations: crosstabs between key columns
- Group-by aggregations: summary stats grouped by categorical columns
- Multi-level grouping: nested groupby with multiple aggregation functions
- Time-series patterns: if date columns exist, trends over time periods

### 5. Advanced Statistical Analysis (Complex)
- Distribution testing: normality tests, distribution fitting
- Segmentation analysis: identifying natural clusters or segments in the data
- Pareto analysis: 80/20 rule (e.g., which 20% of customers drive 80% of revenue)
- Dependency analysis: which columns predict or influence others
- Comparative analysis: differences between groups or time periods

### 6. Custom Insights (Complex)
- Domain-specific queries based on the data's purpose (e.g., customer retention, product performance)
- Derived metrics: ratios, percentages, growth rates
- Threshold-based analysis: how many rows meet certain conditions
- Ranking and sorting: top performers, worst performers, variability


## Output Format
{parser_for_pandas_query_generator.get_format_instructions()}
"""

sys_prompt_for_graph_query_generator = f"""
You are a senior data visualization expert specializing in exploratory data analysis (EDA) and data storytelling.

The user will provide a description of a CSV file. Your task is to generate descriptions of all charts, graphs, and animations needed to produce a comprehensive, visually rich, and interactive data analysis report that reveals trends, patterns, and insights beautifully.

## Your Goal
Create a complete set of visualizations that tell a story about the data—from static charts revealing distributions and relationships, to animated visualizations showing trends and changes over time or dimensions.
Generate 5-10 queries.

## Visualization Categories (Generate Across ALL Categories)

### 1. Static Distribution Visualizations (Simple to Moderate)
- Histograms: distribution of numeric columns, with bin optimization
- Box plots: distribution, outliers, and quartiles per numeric column
- Violin plots: distribution shape with density estimation
- Bar charts: frequency or count of categorical values, sorted by frequency
- Pie charts: proportion/composition of categorical values (use sparingly, only for 2-5 categories)
- KDE plots: smooth distribution visualization for numeric columns

### 2. Relationship & Correlation Visualizations (Moderate)
- Scatter plots: relationships between two numeric columns, with optional color/size encoding
- Correlation heatmap: numeric-to-numeric relationships, with annotations
- Bubble charts: three numeric variables (x, y, size) plus optional color grouping
- Pair plots: multi-variable relationships (grid of scatter plots)
- Categorical scatter: numeric vs categorical with jitter or strip plots
- 2D density plots: bivariate distributions with heatmap/contour overlay

### 3. Comparative Visualizations (Moderate)
- Grouped bar charts: categorical comparison across groups
- Stacked bar charts: composition breakdown by category
- Side-by-side box plots: distribution comparison across groups
- Grouped scatter plots: relationships split by categorical grouping
- Sunburst charts: hierarchical categorical breakdowns (multi-level pie)
- Waterfall charts: cumulative changes or contributions

### 4. Time Series & Trend Visualizations (Moderate to Complex)
- Line charts: trends over time with multiple series if applicable
- Area charts: cumulative trends or stacked areas over time
- Candlestick charts: OHLC data if available (e.g., stock prices)
- Range plots: min/max bands over time periods
- Slope charts: changes between two time points for multiple groups

### 5. Miscellaneous charts
- Any chart as per dataset



## Output format:
{parser_for_graph_query_generator.get_format_instructions()}

## Note - 
Return output strictly in given format do not add image name in query .
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

    return {"pandas_queries": res.queries_description}


async def wrapper_for_schema_generator(state: schema_for_main_graph):
    res = await schema_generator_workflow.ainvoke(
        {"messages": [HumanMessage(content=f'File path = {state["file_path"]}')]}
    )
    # print(res['csv_schema'])
    return {"csv_schema": res["csv_schema"]}


async def wrapper_for_pandas_query_executor(inp):
    query = inp["query"]
    csv_schema = inp["csv_schema"]
    csv_file_path = inp["csv_file_path"]

    messages = HumanMessage(content=f"csv_schema: {csv_schema} \n\n task:{query} \n\n csv_file_path - {csv_file_path}")

    res = await workflow_for_pandas_query.ainvoke(
        {"messages": [messages], "query": query}
    )
    return {"pandas_results": [res["formatted_result"]]}


def fanout_for_pandas_query(state: schema_for_main_graph):
    res = []
    for pd_q in state["pandas_queries"]:
        res.append(
            Send(
                "wrapper_for_pandas_query_executor",
                {"csv_schema": state["csv_schema"], "query": pd_q,'csv_file_path':state['file_path']},
            )
        )
    return res


async def wrapper_for_graph_query_executor(inp):
    task = inp["task"]
    image_name = inp["image_name"]
    csv_file_path = inp["csv_file_path"]
    csv_schema = inp["csv_schema"]

    messages = HumanMessage(content=f"""
        task-{task}
        file_path-{f"{image_folder}/{image_name}"}
        csv_schema-{csv_schema}
        csv_file_path-{csv_file_path}
""")

    res = await workflow_for_graph_query.ainvoke({"messages": [messages]})
    return


def fanout_for_graph_query(state: schema_for_main_graph):
    res = []
    for pd_q in state["graph_queries"].queries_description:
        res.append(
            Send(
                "wrapper_for_graph_query_executor",
                {
                    "csv_schema": state["csv_schema"],
                    "task": pd_q.queries_description,
                    "image_name": pd_q.image_name,
                    "csv_file_path": state['file_path'],
                },
            )
        )
    return res


def dummy_collector(state: schema_for_main_graph):
    return


class schema_for_markdown_generator(BaseModel):
    markdown: str = Field(..., description="markdown file")


parser_for_markdown_generator = PydanticOutputParser(
    pydantic_object=schema_for_markdown_generator
)

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


def markdown_generator(state: schema_for_main_graph):
    po = ""
    for i in state["pandas_results"]:
        po = po + f"query= {i.query}" + f"\n result= {i.result}\n\n"

    gq = ""
    for i in state["graph_queries"].queries_description:
        gq = (
            gq
            + "\n"
            + i.queries_description
            + "\n"
            + f"File path = {image_folder}/{i.image_name}"
            + "\n"
        )
    pr = f"""
    Csv schema - 
    {state['csv_schema']}



    Pandas queries and output - 
    {po}

    
    graph queries and output - 
    {gq}
    """

    # print(pr)
    pr = [
        SystemMessage(content=sys_prompt_for_markdown_generator),
        HumanMessage(content=pr),
    ]
    res = model_for_markdown_generator.invoke(pr)
    res = parser_for_markdown_generator.invoke(res)

    with open(f"{image_folder}/markdown.md", "w") as f:
        f.write(res.markdown)

    return {"markdown": res.markdown}


graph = StateGraph(schema_for_main_graph)

graph.add_node("wrapper_for_schema_generator", wrapper_for_schema_generator)
graph.add_node("pandas_query_generator", pandas_query_generator)
graph.add_node("graph_query_generator", graph_query_generator)
graph.add_node("wrapper_for_pandas_query_executor", wrapper_for_pandas_query_executor)
graph.add_node("wrapper_for_graph_query_executor", wrapper_for_graph_query_executor)
graph.add_node("dummy_collector", dummy_collector)
graph.add_node("markdown_generator", markdown_generator)
# graph.add_node('tools',ToolNode(tools=[run_pandas_queries,run_graph_queries]))

graph.add_edge(START, "wrapper_for_schema_generator")
graph.add_edge("wrapper_for_schema_generator", "pandas_query_generator")
graph.add_edge("wrapper_for_schema_generator", "graph_query_generator")

graph.add_conditional_edges(
    "pandas_query_generator",
    fanout_for_pandas_query,
    ["wrapper_for_pandas_query_executor"],
)
graph.add_edge("wrapper_for_pandas_query_executor", "dummy_collector")

graph.add_conditional_edges(
    "graph_query_generator",
    fanout_for_graph_query,
    ["wrapper_for_graph_query_executor"],
)

graph.add_edge("wrapper_for_graph_query_executor", "dummy_collector")
graph.add_edge("dummy_collector", "markdown_generator")
graph.add_edge("markdown_generator", END)


workflow = None
conn = None


async def d():
    global workflow, conn
    conn = await aiosqlite.connect("checkpoints.db")
    checkpointer = AsyncSqliteSaver(conn)
    await checkpointer.setup()
    workflow = graph.compile(checkpointer=checkpointer)
    


asyncio.run(d())


async def run_workflow():
    config = {"configurable": {"thread_id": "3"}}
    try:
        r = await workflow.ainvoke(
            {
                "file_path": "C:\\Users\\panka\\genai_project\\data_analysis_agent\\data\\Iris.csv"
            },
            config=config,
        )
    except Exception as E:
        print(E)
        r = await workflow.ainvoke(None, config=config)

    return r


async def stream_workflow():
    try:
        config = {"configurable": {"thread_id": "5"}}
        inp = {
            "file_path": "C:\\Users\\panka\\genai_project\\data_analysis_agent\\data\\Iris.csv"
        }
        async for chunk in workflow.astream(inp,config=config,stream_mode=['updates']):
        # async for chunk in workflow.astream(
        #     None, config=config, stream_mode=["updates"]
        # ):
            a, b = chunk
            if a == "updates":
                print(f"{list(b.keys())[0]} node is competed")
    except Exception as E:
        print(E)
    finally:
        await conn.close()


if __name__ == "__main__":
    # res = asyncio.run(run_workflow())
    res = asyncio.run(stream_workflow())
