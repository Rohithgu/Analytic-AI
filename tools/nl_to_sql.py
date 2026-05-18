import os
from pathlib import Path

import pandas as pd


def _gemini_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        import google.generativeai as genai
    except ImportError:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


def convert_to_sql(question: str, file_path: str, table_name: str = "data") -> str:
    """Convert a natural-language question into SQL for the given dataset."""
    path = Path(file_path)
    if not path.exists():
        return f"File not found: {file_path}"

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    elif path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        return f"Unsupported file type: {path.suffix}"

    schema = ", ".join(f"{col} ({dtype})" for col, dtype in df.dtypes.items())
    prompt = f"""You are a SQL expert. The data is available as DuckDB table "{table_name}".

Columns: {schema}

Question: {question}

Reply with only executable SQL. Use table name "{table_name}"."""

    model = _gemini_model()
    if model is None:
        return (
            "GEMINI_API_KEY is not set. Set it in the environment to use natural-language to SQL."
        )

    try:
        response = model.generate_content(prompt)
        return (response.text or "").strip()
    except Exception as exc:
        return f"Error generating SQL: {exc}"
