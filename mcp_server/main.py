from fastmcp import FastMCP
from pydantic import Field
from typing import List
import pandas as pd

mcp = FastMCP()


@mcp.tool()
def dummy_tool():
    return "sucess"


@mcp.tool()
def run_pandas_queries(
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
    try:
        scope = {}
        exec(queries, {}, scope)
        result = {"status": "success"}
        for var in variables_to_return:
            result[var] = str(scope.get(var, None))
        return result
    except Exception as e:
        return {"status": "failed", "error": str(e)}


@mcp.tool()
def run_graph_queries(
    queries: str = Field(
        ...,
        description="Multiple plotly or pandas queries separated by newlines (\\n). Each line should be a valid Python statement.",
    ),
):
    """
    Executes a multi-line Plotly graphing script in an isolated scope and saves
    the resulting figure as a PNG image.

    This tool is designed for stepwise chart construction — you can build and
    layer Plotly traces across multiple lines, customize layout, and persist
    the final figure by calling fig.write_image('<path>.png') within the query.

    Args:
        queries (str): A newline-separated string of valid Python/Plotly statements.
                       Variables assigned in earlier lines are accessible in later lines.
                       The script must assign the figure to `fig` and save it using
                       fig.write_image('<path>.png').

    Returns:
        dict: On success — {"status": "success"}
              On failure — {"status": "failed", "error": "<error message>"}

    Eg:
        Input:
            queries = \"\"\"
                import plotly.express as px
                import pandas as pd
                df = pd.read_csv('iris.csv')
                fig = px.scatter(df, x='SepalLengthCm', y='SepalWidthCm', color='Species')
                fig.update_layout(title='Iris Sepal Dimensions')
                fig.write_image('iris_scatter.png')
            \"\"\"

        Output:
            {"status": "success"}
    """
    try:
        scope = {}
        exec(queries, {}, scope)
        result = {"status": "success"}
        return result
    except Exception as e:
        return {"status": "failed", "error": str(e)}


if __name__ == "__main__":
    mcp.run()
