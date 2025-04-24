

import pandas as pd
import pyodbc
import google.generativeai as genai

# ✅ Configure Gemini
genai.configure(api_key="Shubh api key") 
model = genai.GenerativeModel("gemini-1.5-pro")

# ✅ SQL Server connection to Tcs_data DB
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=LAPTOP-SHUBH BHARDWAJ\\SQLEXPRESS;"
    "DATABASE=Tcs_data;"
    "Trusted_Connection=yes;"
)

# ✅ Get samples from all 3 tables
def get_all_samples():
    with pyodbc.connect(conn_str) as conn:
        customer_df = pd.read_sql("SELECT TOP 3 * FROM CustomerTable", conn)
        sales_df = pd.read_sql("SELECT TOP 3 * FROM SalesTable", conn)
        transaction_df = pd.read_sql("SELECT TOP 3 * FROM TransactionLog", conn)
    return customer_df, sales_df, transaction_df

# ✅ Generate SQL using Gemini
def generate_sql_query(user_question, customer_df, sales_df, transaction_df):
    prompt = f"""
You are an expert SQL Server assistant. Write a valid SQL Server query based on the schema, column types, and relationships provided below.

📌 Table Relationships:
- One Customer can have many Sales (CustomerTable.CustomerID → SalesTable.CustomerID)
- One Sale can have one or more Transactions (SalesTable.SaleID → TransactionLog.SaleID)

Table: CustomerTable  
Columns: {list(customer_df.columns)}  
Sample Rows: {customer_df.to_dict(orient='records')}

Table: SalesTable  
Columns: {list(sales_df.columns)}  
Sample Rows: {sales_df.to_dict(orient='records')}

Table: TransactionLog  
Columns: {list(transaction_df.columns)}  
Sample Rows: {transaction_df.to_dict(orient='records')}


💬 User Question: {user_question}

📣 Important Rules:
- Use JOINs where appropriate.
- Use GROUP BY, ORDER BY, and subqueries as needed.
- Use fully qualified table and column names for clarity.
- Do not use markdown or explanations.
- Return only valid SQL Server SQL.
"""

    response = model.generate_content(prompt)
    return response.text.strip().replace("```sql", "").replace("```", "").strip()

# ✅ Execute SQL query
def run_query(sql):
    try:
        with pyodbc.connect(conn_str) as conn:
            df = pd.read_sql(sql, conn)
        return df
    except Exception as e:
        return f"❌ Error: {e}"
