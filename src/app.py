import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


import streamlit as st
from src.config import MODEL_CONFIGS, get_model_names
from src.models import get_model
from src.prompts.templates import build_prompt
from src.prompts.tasks import TASKS

st.set_page_config(page_title="AI Code Correctness", layout="wide")
st.markdown("""
    <style>
    code {
        font-size: 16px !important;
        line-height: 1.6 !important;
    }
    table {
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("AI Code Correctness and Usability")

col1, col2, col3 = st.columns(3)

with col1:
    task_name = st.selectbox('Task', list(TASKS.keys()))

with col2:
    language = st.selectbox("Language", ['Python', 'Lean 4'])

with col3:
    style = st.selectbox("Prompt Style", ['naive', 'structured', 'chain_of_thought'])

selected_models = st.multiselect("Select Models", get_model_names(), default= 'deepseek-v4-pro')

# --- Prompt Preview ---
task = TASKS[task_name]
prompt = build_prompt(style=style, language=language, **task)

with st.expander("Preview Prompt"):
    st.text(prompt)

# --- Generate ---
if st.button("Generate from the Selected Models"):
    results = []

    with st.spinner("Calling models..."):
        for model_name in selected_models:
            model = get_model(model_name)
            result = model.generate(prompt)
            results.append(result)

    # --- Summary Portion ---
    st.subheader("Summary")
    summary_data = []
    for r in results:
        summary_data.append(
            {
                "Model": r.model_name,
                "Time (s)": f"{r.response_time:.2f}",
                "Status": "Success" if r.error is None else f"{r.error}"
            }
        )
    st.table(summary_data)

    # --- To Print Individual Results ---
    st.subheader("Responses")
    code_language = "python" if language == "Python" else "lean4"

    for r in results:
        with st.expander(f"{r.model_name} ({r.response_time:.2f}s) {"Success" if r.error is None else "Error"}"):
            if r.error:
                st.error(r.error)
            else:
                st.code(r.response, language=code_language)


