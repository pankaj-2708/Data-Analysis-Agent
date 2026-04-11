from fastmcp import FastMCP
from pydantic import Field
from typing import List
import pandas as pd
import subprocess
import asyncio

mcp = FastMCP()

timeout=60

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
    except asyncio.TimeoutError:
        return {"status": "failed", "error": f"Execution timed out after {timeout} seconds"}
    
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
