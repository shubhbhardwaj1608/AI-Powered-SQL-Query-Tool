import streamlit as st
import pandas as pd
from gemini_multitable import get_all_samples, generate_sql_query, run_query
import plotly.express as px
import time
import base64

# --- Page Config ---
st.set_page_config(page_title="Gemini + Multi-Table SQL App", layout="wide")

# --- View Table Samples Dropdown ---
cust_df, sale_df, trans_df = get_all_samples()
table_option = st.selectbox("📋 View Sample Table Data", ["CustomerTable", "SalesTable", "TransactionLog"])

if table_option == "CustomerTable":
    st.dataframe(cust_df.head(5))
elif table_option == "SalesTable":
    st.dataframe(sale_df.head(5))
elif table_option == "TransactionLog":
    st.dataframe(trans_df.head(5))


st.title("📊 Gemini + SSMS | Ask Anything from Multi-Table Data")

# --- Background Images ---
def add_bg_from_local(main_bg, sidebar_bg):
    with open(main_bg, "rb") as image_file:
        main_bg_base64 = base64.b64encode(image_file.read()).decode()
    with open(sidebar_bg, "rb") as image_file:
        sidebar_bg_base64 = base64.b64encode(image_file.read()).decode()

    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{main_bg_base64}");
            background-size: cover;
        }}
        section[data-testid="stSidebar"] > div:first-child {{
            background-image: url("data:image/jpg;base64,{sidebar_bg_base64}");
            background-size: cover;
        }}
        </style>
    """, unsafe_allow_html=True)

add_bg_from_local("bg_main.jpg", "bg_sidebar.jpg")

# --- Session State Initialization ---
if "history" not in st.session_state:
    st.session_state.history = []
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

# --- Clear Chat Logic BEFORE Text Input is Defined ---
if st.session_state.clear_input:
    st.session_state.clear_input = False
    st.session_state.history = []
    user_question = ""
else:
    user_question = st.session_state.get("user_question", "")

# --- Sidebar ---
with st.sidebar:
    st.markdown("## ⚙ App Settings")

    st.markdown("### 🧠 Query History")
    if st.session_state.history:
        for i, (q, s, _) in enumerate(reversed(st.session_state.history), 1):
            with st.expander(f"🕘 Query {i}"):
                st.markdown(f"Q: {q}")
                st.code(s, language="sql")
    else:
        st.info("No queries yet!")

    st.markdown("---")
    if st.checkbox("🔐 Show Gemini API Key"):
        st.code("SHUBH API key", language="text")
    else:
        st.text("🔐 Gemini API Key: Hidden")

    st.markdown("---")
    selected_member = st.selectbox(
        "👥 Team Members",
        ["Mandakini Srivastava", "Navansh Mishra", "Shubh Bhardwaj"]
    )

# --- Text Input ---
user_question = st.text_input("🧠 Ask a Question:", value=user_question, key="user_question")

# --- Buttons ---
col1, col2 = st.columns([1, 1])
with col1:
    run_clicked = st.button("▶ Run Query")
with col2:
    clear_clicked = st.button("🧹 Clear Chat")

# --- Feedback Slider ---
st.markdown("### ⭐ Rate Your Experience")
rating = st.select_slider('Rate us:', ['', 'Bad', 'Good', 'Excellent'], label_visibility="visible")
if rating and rating != '':
    st.success("✅ Thanks for your valuable feedback!")

# --- Clear Chat Clicked ---
if clear_clicked:
    st.session_state.sql_query = ""
    st.session_state.query_result = None
    st.session_state.history = []
    st.session_state.clear_input = True
    st.warning("⚠ Chat cleared!")

# --- Run Query Logic ---
if run_clicked and user_question.strip():
    with st.spinner("⏳ Please wait, Gemini is thinking..."):
        cust_df, sale_df, trans_df = get_all_samples()
        sql = generate_sql_query(user_question, cust_df, sale_df, trans_df)
        result_df = run_query(sql)
        st.session_state.history.append((user_question, sql, result_df))
    st.success("✅ Query executed successfully!")

# --- Progress Bar ---
if run_clicked:
    progress = st.progress(0)
    for percent in range(1, 101):
        time.sleep(0.005)
        progress.progress(percent)

# --- Display Result ---
if st.session_state.history:
    question, sql_code, result = st.session_state.history[-1]

    st.subheader("🧠 Gemini Generated SQL")
    st.code(sql_code, language="sql")

    if isinstance(result, pd.DataFrame):
        st.subheader("📋 Query Result")
        st.dataframe(result)

        if not result.empty:
            st.markdown("### 📈 Visualize Result")
            chart_type = st.selectbox("Choose Chart Type", ["None", "Line", "Bar", "Pie", "Box"])

            num_cols = result.select_dtypes(include='number').columns.tolist()
            all_cols = result.columns.tolist()

            if chart_type == "Line":
                x = st.selectbox("X-axis", all_cols, key="line_x")
                y = st.multiselect("Y-axis (numeric)", num_cols, key="line_y")
                if x and y:
                    st.line_chart(result.set_index(x)[y])

            elif chart_type == "Bar":
                x = st.selectbox("X-axis", all_cols, key="bar_x")
                y = st.selectbox("Y-axis", num_cols, key="bar_y")
                if x and y:
                    st.bar_chart(result[[x, y]].set_index(x))

            elif chart_type == "Pie":
                labels = st.selectbox("Label Column", all_cols, key="pie_labels")
                values = st.selectbox("Value Column", num_cols, key="pie_values")
                fig = px.pie(result, names=labels, values=values)
                st.plotly_chart(fig)

            elif chart_type == "Box":
                y = st.selectbox("Y (numeric)", num_cols, key="box_y")
                x = st.selectbox("X (category)", all_cols, key="box_x")
                fig = px.box(result, x=x, y=y)
                st.plotly_chart(fig)
    else:
        st.error(result)

# --- Footer ---
st.markdown("---")
st.caption("© 2025 | Created by Team | Streamlit + Gemini + SSMS_SQL Server")
