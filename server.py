from mcp.server.fastmcp import FastMCP

from tools.csv_analyzer import analyze_csv
from tools.eda_tool import perform_eda
from tools.sql_tool import run_sql_query
from tools.nl_to_sql import convert_to_sql

mcp = FastMCP("DataAnalysisMCP")

mcp.tool()(analyze_csv)
mcp.tool()(perform_eda)
mcp.tool()(run_sql_query)
mcp.tool()(convert_to_sql)

if __name__ == "__main__":
    mcp.run()