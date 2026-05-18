from pathlib import Path

import duckdb
import pandas as pd


def run_sql_query(query: str, file_path: str, table_name: str = "data") -> str:
    """Run a SQL query against a CSV or Excel file using DuckDB."""
    path = Path(file_path)
    if not path.exists():
        return f"File not found: {file_path}"

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    elif path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        return f"Unsupported file type: {path.suffix}"

    conn = duckdb.connect()
    conn.register(table_name, df)
    try:
        result = conn.execute(query).fetchdf()
    except Exception as exc:
        return f"SQL error: {exc}"
    finally:
        conn.close()

    return result.to_string()
