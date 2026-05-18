from pathlib import Path

import pandas as pd


def _load_table(file_path: str) -> pd.DataFrame:
    path = Path(file_path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")


def perform_eda(file_path: str) -> str:
    """Run exploratory data analysis on a CSV or Excel file."""
    df = _load_table(file_path)
    numeric = df.select_dtypes(include="number")

    sections = [
        "=== Missing values ===",
        df.isnull().sum().to_string(),
        "",
        f"=== Duplicate rows: {df.duplicated().sum()} ===",
        "",
        "=== Describe ===",
        df.describe(include="all").to_string(),
    ]

    if not numeric.empty:
        sections.extend(
            [
                "",
                "=== Correlation (numeric) ===",
                numeric.corr().to_string(),
            ]
        )

    return "\n".join(sections)
