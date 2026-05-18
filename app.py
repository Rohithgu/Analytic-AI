import os
import streamlit as st
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import plotly.express as px
import google.generativeai as genai
from textblob import TextBlob
from wordcloud import WordCloud
import nltk
import re

# ==========================
# Download NLTK Data
# ==========================

nltk.download('punkt')

# ==========================
# Gemini API Configuration
# ==========================

GEMINI_API_KEY = "AIzaSyBXDP7r33_uAlXjnW-zUSp-L_uvM6FVd9w"

def _gemini_api_key():

    if GEMINI_API_KEY:
        return GEMINI_API_KEY

    key = os.environ.get("AIzaSyBXDP7r33_uAlXjnW-zUSp-L_uvM6FVd9w")

    if key:
        return key

    try:
        return st.secrets["AIzaSyBXDP7r33_uAlXjnW-zUSp-L_uvM6FVd9w"]

    except:
        return None


_gemini_key = _gemini_api_key()

if _gemini_key:

    genai.configure(api_key=_gemini_key)

    model = genai.GenerativeModel("gemini-2.5-flash")

else:

    model = None


def _parse_ai_sections(text):
    """Extract CODE, ANSWER, and EXPLANATION from model output."""
    sections = {"code": "", "answer": "", "explanation": ""}
    if not text:
        return sections

    pattern = re.compile(
        r"(?is)^\s*(CODE|ANSWER|EXPLANATION)\s*:\s*(.*?)(?=^\s*(?:CODE|ANSWER|EXPLANATION)\s*:|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for label, body in pattern.findall(text):
        key = label.lower()
        sections[key] = body.strip()

    if not sections["code"] and not sections["answer"]:
        sections["code"] = text.strip()

    return sections


def _clean_code(code_text):
    cleaned = code_text
    for token in ("```sql", "```python", "```pandas", "```"):
        cleaned = cleaned.replace(token, "")
    return cleaned.replace("```", "").strip()


def _run_code_for_answer(code_type, code_text, dataframe):
    """Execute generated code and return a result table when possible."""
    if not code_text:
        return None, "No code was generated to run."

    try:
        if code_type == "SQL":
            return duckdb.query(code_text).to_df(), None

        if code_type in ("Python", "Pandas"):
            namespace = {"filtered_df": dataframe, "pd": pd, "duckdb": duckdb}
            exec(code_text, namespace)
            if "result" in namespace:
                result = namespace["result"]
                if isinstance(result, pd.DataFrame):
                    return result, None
                return pd.DataFrame({"answer": [result]}), None
            return None, "Code ran but no `result` variable was returned. Assign your output to `result`."

        return None, f"Run the {code_type} code in its tool to see the data answer."

    except Exception as exc:
        return None, str(exc)

# ==========================
# Page Configuration
# ==========================

st.set_page_config(
    page_title="Analytica AI",
    layout="wide"
)

st.title("Analytica AI")

st.markdown(
    "### AI-Powered Data Analytics, NLP & SQL Intelligence Platform"
)

# ==========================
# Upload Multiple Files
# ==========================

uploaded_files = st.file_uploader(
    "Upload CSV or Excel Files",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

all_dataframes = {}

if uploaded_files:

    # ==========================
    # Read All Files
    # ==========================

    for uploaded_file in uploaded_files:

        file_name = uploaded_file.name

        # CSV Files

        if file_name.endswith(".csv"):

            df = pd.read_csv(uploaded_file)

            table_name = file_name.replace(".csv", "")

            all_dataframes[table_name] = df

        # Excel Files

        elif file_name.endswith(".xlsx"):

            excel_file = pd.ExcelFile(uploaded_file)

            for sheet in excel_file.sheet_names:

                df = pd.read_excel(
                    uploaded_file,
                    sheet_name=sheet
                )

                table_name = (
                    f"{file_name.replace('.xlsx', '')}_{sheet}"
                )

                all_dataframes[table_name] = df

    # ==========================
    # Dataset Selector
    # ==========================

    st.sidebar.header("Datasets")

    selected_table = st.sidebar.selectbox(
        "Choose Dataset",
        list(all_dataframes.keys())
    )

    df = all_dataframes[selected_table]

    filtered_df = df.copy()

    # ==========================
    # Sidebar Filters
    # ==========================

    st.sidebar.header("Filters")

    categorical_cols = (
        filtered_df
        .select_dtypes(include='object')
        .columns
    )

    for col in categorical_cols:

        unique_values = (
            filtered_df[col]
            .dropna()
            .unique()
        )

        selected_values = st.sidebar.multiselect(
            f"Filter {col}",
            unique_values,
            default=unique_values
        )

        filtered_df = filtered_df[
            filtered_df[col].isin(selected_values)
        ]

    # ==========================
    # Dataset Preview
    # ==========================

    st.subheader("Dataset Preview")

    st.write(filtered_df.head())

    # ==========================
    # Summary Statistics
    # ==========================

    st.subheader("Summary Statistics")

    st.write(filtered_df.describe())

    # ==========================
    # KPI Dashboard
    # ==========================

    st.subheader("KPI Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Rows",
        filtered_df.shape[0]
    )

    col2.metric(
        "Total Columns",
        filtered_df.shape[1]
    )

    numeric_cols = (
        filtered_df
        .select_dtypes(include='number')
    )

    if not numeric_cols.empty:

        first_numeric = numeric_cols.columns[0]

        col3.metric(
            "Average Value",
            round(
                filtered_df[first_numeric].mean(),
                2
            )
        )

        col4.metric(
            "Maximum Value",
            round(
                filtered_df[first_numeric].max(),
                2
            )
        )

    # ==========================
    # AI Generated Insights
    # ==========================

    st.subheader("AI Generated Insights")

    insights = []

    missing = (
        filtered_df
        .isnull()
        .sum()
        .sum()
    )

    if missing > 0:

        insights.append(
            f"Dataset contains {missing} missing values."
        )

    else:

        insights.append(
            "No missing values detected."
        )

    duplicates = filtered_df.duplicated().sum()

    if duplicates > 0:

        insights.append(
            f"Dataset contains {duplicates} duplicate rows."
        )

    else:

        insights.append(
            "No duplicate rows found."
        )

    for col in numeric_cols.columns:

        avg = filtered_df[col].mean()

        maximum = filtered_df[col].max()

        minimum = filtered_df[col].min()

        insights.append(
            f"{col}: Average = {avg:.2f}, "
            f"Max = {maximum}, Min = {minimum}"
        )

    for insight in insights:

        st.success(insight)

    # ==========================
    # Automated EDA
    # ==========================

    st.subheader("Automated EDA")

    st.write("Missing Values")

    st.write(filtered_df.isnull().sum())

    st.write("Duplicate Rows")

    st.write(filtered_df.duplicated().sum())

    st.write("Data Types")

    st.write(filtered_df.dtypes)

    if not numeric_cols.empty:

        st.write("Correlation Matrix")

        st.write(
            numeric_cols.corr()
        )

    # ==========================
    # Histograms
    # ==========================

    st.subheader("Histograms")

    for col in numeric_cols.columns:

        fig, ax = plt.subplots()

        ax.hist(filtered_df[col])

        ax.set_title(col)

        st.pyplot(fig)

    # ==========================
    # Interactive Visualizations
    # ==========================

    st.subheader("Interactive Visualizations")

    if (
        len(numeric_cols.columns) > 0
        and
        len(categorical_cols) > 0
    ):

        category_col = categorical_cols[0]

        value_col = numeric_cols.columns[0]

        grouped_data = (
            filtered_df
            .groupby(category_col)[value_col]
            .sum()
            .reset_index()
        )

        # Bar Chart

        bar_fig = px.bar(
            grouped_data,
            x=category_col,
            y=value_col,
            title=f"{value_col} by {category_col}"
        )

        st.plotly_chart(bar_fig)

        # Pie Chart

        pie_fig = px.pie(
            grouped_data,
            names=category_col,
            values=value_col,
            title=f"{value_col} Distribution"
        )

        st.plotly_chart(pie_fig)

        # Line Chart

        line_fig = px.line(
            grouped_data,
            x=category_col,
            y=value_col,
            title=f"{value_col} Trend"
        )

        st.plotly_chart(line_fig)

    # ==========================
    # AI Code Generator
    # ==========================

    st.subheader("AI Code Generator")

    code_type = st.selectbox(
        "Select Code Type",
        [
            "SQL",
            "Python",
            "Pandas",
            "Power BI DAX",
            "Excel Formula"
        ]
    )

    user_question = st.text_input(
        "Ask your question",
        "Show top 5 products by sales"
    )

    if st.button("Generate AI Code"):

        if model is None:

            st.error(
                "Gemini API key not found."
            )

        else:

            try:

                prompt = f'''
You are an expert {code_type} developer and data analyst.

Dataset name: filtered_df
Columns: {list(filtered_df.columns)}

User question: {user_question}

Reply using exactly these three sections (no extra sections):

ANSWER:
<Direct answer to the user question in plain English. Include key numbers or rankings if the question asks for them.>

CODE:
<Only executable {code_type} code. For Python/Pandas, assign the final output to a variable named `result`.>

EXPLANATION:
<Short business explanation of what the code does and why it answers the question.>
'''

                response = model.generate_content(prompt)

                sections = _parse_ai_sections(response.text)
                code_part = _clean_code(sections["code"])
                answer_part = sections["answer"] or (
                    "No direct answer was returned. See the data result below."
                )
                explanation_part = sections["explanation"] or (
                    "No explanation generated."
                )

                result_df, run_error = _run_code_for_answer(
                    code_type, code_part, filtered_df
                )

                # ==========================
                # Answer (shown first)
                # ==========================

                st.subheader("Answer")

                st.success(answer_part)

                if result_df is not None:
                    st.markdown("**Data result**")
                    st.dataframe(result_df, use_container_width=True)
                elif run_error and code_type in ("SQL", "Python", "Pandas"):
                    st.warning(f"Could not run code for data result: {run_error}")

                # ==========================
                # Generated Code
                # ==========================

                st.subheader("Generated Code")

                lang = "sql" if code_type == "SQL" else "python"
                st.code(code_part, language=lang)

                # ==========================
                # Business Explanation
                # ==========================

                st.subheader("Business Explanation")

                st.info(explanation_part)

            except Exception as e:

                st.error(e)

    # ==========================
    # Self Code Writing Section
    # ==========================

    st.subheader("Write Your Own Code")

    manual_code_type = st.selectbox(
        "Choose Manual Code Type",
        [
            "Python",
            "SQL"
        ]
    )

    manual_code = st.text_area(
        "Write Your Code Here",
        height=300
    )

    if st.button("Run Your Code"):

        # Run SQL

        if manual_code_type == "SQL":

            try:

                result = duckdb.query(
                    manual_code
                ).to_df()

                st.subheader("SQL Result")

                st.write(result)

            except Exception as e:

                st.error(e)

        # Run Python

        elif manual_code_type == "Python":

            try:

                local_vars = {
                    "pd": pd,
                    "filtered_df": filtered_df
                }

                exec(manual_code, {}, local_vars)

                st.success(
                    "Python code executed successfully."
                )

            except Exception as e:

                st.error(e)

    # ==========================
    # Text Mining Analysis
    # ==========================

    st.subheader("Text Mining Analysis")

    text_columns = (
        filtered_df
        .select_dtypes(include='object')
        .columns
    )

    if len(text_columns) > 0:

        selected_text_col = st.selectbox(
            "Select Text Column",
            text_columns
        )

        text_data = (
            filtered_df[selected_text_col]
            .dropna()
            .astype(str)
        )

        combined_text = " ".join(text_data)

        # Sentiment Analysis

        polarity = (
            TextBlob(combined_text)
            .sentiment
            .polarity
        )

        if polarity > 0:

            st.success(
                "Overall Sentiment: Positive"
            )

        elif polarity < 0:

            st.error(
                "Overall Sentiment: Negative"
            )

        else:

            st.warning(
                "Overall Sentiment: Neutral"
            )

        # Word Cloud

        st.subheader("Word Cloud")

        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white'
        ).generate(combined_text)

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.imshow(wordcloud)

        ax.axis("off")

        st.pyplot(fig)

        # Most Common Words

        st.subheader("Most Common Words")

        cleaned_text = re.sub(
            r'[^a-zA-Z ]',
            '',
            combined_text.lower()
        )

        words = cleaned_text.split()

        word_freq = (
            pd.Series(words)
            .value_counts()
            .head(10)
        )

        st.write(word_freq)

    else:

        st.warning(
            "No text columns found in dataset."
        )

    # ==========================
    # Download Filtered Data
    # ==========================

    st.subheader("Download Filtered Data")

    csv = (
        filtered_df
        .to_csv(index=False)
        .encode('utf-8')
    )

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='filtered_data.csv',
        mime='text/csv'
    )