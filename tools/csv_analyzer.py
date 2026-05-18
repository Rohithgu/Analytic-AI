from pathlib import Path

import pandas as pd


def analyze_csv(file_path: str) -> str:
    """Load a CSV or Excel file and return a short structural summary."""
    path = Path(file_path)
    if not path.exists():
        return f"File not found: {file_path}"

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    elif path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        return f"Unsupported file type: {path.suffix}"

    lines = [
        f"File: {path.name}",
        f"Rows: {len(df)}, Columns: {len(df.columns)}",
        f"Columns: {', '.join(df.columns.astype(str))}",
        "",
        "Dtypes:",
        df.dtypes.to_string(),
        "",
        "Preview:",
        df.head(5).to_string(),
    ]
    return "\n".join(lines)
