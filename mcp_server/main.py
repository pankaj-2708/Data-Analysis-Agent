from fastmcp import FastMCP
from pydantic import Field
from typing import List
import pandas as pd
import subprocess
import asyncio

mcp = FastMCP()

timeout=10

@mcp.tool()
def dummy_tool():
    return "sucess"


@mcp.tool()
async def run_pandas_queries(
    queries: str = Field(
        ...,
        description="Multiple pandas queries separated by newlines (\\n). Each line should be a valid Python statement. Assign intermediate results to named variables for retrieval.",
    ),
    variables_to_return: List[str] = Field(
        ...,
        description="List of variable names defined in the queries whose values should be returned. Variables not found in scope will return None.",
    ),
) -> dict:
    """
    Executes a multi-line pandas query string in an isolated scope and returns
    the values of specified intermediate variables.

    This tool uses exec function of python so write your queries compaitable with it.

    This tool is designed for stepwise data exploration — you can chain multiple
    pandas operations across lines and selectively retrieve any named variable
    from the execution scope.

    Args:
        queries (str): A newline-separated string of valid Python/pandas statements.
                       Variables assigned in earlier lines are accessible in later lines.

        variables_to_return (List[str]): Names of variables from the query scope to
                                         include in the response. Any name not found
                                         in scope will be returned as None.

    Returns:
        dict: On success — {"status": "success", "<var1>": <value>, "<var2>": <value>, ...}
              On failure — {"status": "failed", "error": "<error message>"}

    Eg:
        Input:
            queries = \"\"\"
                import pandas as pd
                df = pd.read_csv('iris.csv')
                columns = df.columns
                shape = df.shape
            \"\"\"
            variables_to_return = ['columns', 'shape']

        Output:
            {
                'status': 'success',
                'columns': Index(['Id', 'SepalLengthCm', ...], dtype='object'),
                'shape': (150, 6)
            }
    """
    scope = {}
    def exec_code():
        exec(queries, {}, scope)
        
    try:

        await asyncio.wait_for(asyncio.to_thread(exec_code), timeout=timeout)
        exec(queries, {}, scope)
        result = {"status": "success"}
        for var in variables_to_return:
            result[var] = str(scope.get(var, None))
        return result
    except Exception as e:
        return {"status": "failed", "error": str(e)}


@mcp.tool()
async def run_graph_queries(
    queries: str = Field(
        ...,
        description="Multiple matplotlib/pandas statements separated by newlines (\\n). Each line must be a valid Python statement.",
    ),
):
    """
Executes a multi-line Matplotlib script using exec() and saves the chart as PNG.

    Rules:
        - Use plt.style.use('seaborn-v0_8-whitegrid') for clean background
        - Set figure size: plt.figure(figsize=(10, 6))
        - Add title, xlabel, ylabel with fontsize=13+
        - Save with: plt.savefig('<path>.png', dpi=150, bbox_inches='tight')
        - Always end with plt.close()

    Args:
        queries (str): Newline-separated Matplotlib/pandas statements.
                       Must save the figure using plt.savefig('<path>.png').

    Returns:
        {"status": "success"} or {"status": "failed", "error": "<message>"}

    Example:
        queries = \"\"\"
            import matplotlib.pyplot as plt
            import pandas as pd
            plt.style.use('seaborn-v0_8-whitegrid')
            df = pd.read_csv('iris.csv')
            plt.figure(figsize=(10, 6))
            plt.scatter(df['SepalLengthCm'], df['SepalWidthCm'], alpha=0.8)
            plt.title('Iris Sepal Dimensions', fontsize=16, fontweight='bold')
            plt.xlabel('Sepal Length (cm)', fontsize=13)
            plt.ylabel('Sepal Width (cm)', fontsize=13)
            plt.tight_layout()
            plt.savefig('iris_scatter.png', dpi=150, bbox_inches='tight')
            plt.close()
        \"\"\"
    """
    scope = {}
    def exec_code():
        exec(queries, {}, scope)
        
    try:

        await asyncio.wait_for(asyncio.to_thread(exec_code), timeout=timeout)
        exec(queries, {}, scope)
        result = {"status": "success"}
        return result
    except Exception as e:
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    mcp.run()
