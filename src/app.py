import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from src.config import MODEL_CONFIGS, get_model_names
from src.models import get_model
from src.prompts.templates import build_prompt
from src.prompts.tasks import TASKS
from src.logging.db import save_run

MAX_ATTEMPTS = 5

st.set_page_config(page_title="AI Code Correctness", layout="wide")
st.title("AI Code Correctness and Usability")

col1, col2, col3 = st.columns(3)

with col1:
    task_name = st.selectbox('Task', list(TASKS.keys()))

with col2:
    language = st.selectbox("Language", ['Python', 'Lean 4'])

with col3:
    style = st.selectbox("Prompt Style", ['naive', 'structured', 'chain_of_thought'])

selected_models = st.multiselect("Select Models", get_model_names(), default='deepseek-v4-pro')

# --- Prompt (editable) ---
task = TASKS[task_name]
base_prompt = build_prompt(style=style, language=language, **task)

prompt = st.text_area(
    "Prompt (editable)",
    value=base_prompt,
    height=200,
    key=f"prompt_{task_name}_{language}_{style}",
)

# --- Initialize session state ---
if "results" not in st.session_state:
    st.session_state.results = {}

# --- Generate ---
if st.button("Generate from the Selected Models"):
    st.session_state.results = {}

    for model_name in selected_models:
        with st.spinner(f"Calling {model_name}..."):
            model = get_model(model_name)
            result = model.generate(prompt)

            run_id = save_run(
                model_name=result.model_name,
                task_name=task_name,
                language=language,
                prompt_style=style,
                prompt_text=prompt,
                response=result.response,
                response_time=result.response_time,
                error=result.error,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
            )

            st.session_state.results[model_name] = {
                "attempts": [(result, run_id)],
                "parent_run_id": run_id,
            }

# --- Display Results ---
if st.session_state.results:
    st.subheader("Summary")
    summary_data = []
    for model_name, data in st.session_state.results.items():
        latest_result, latest_rid = data["attempts"][-1]
        attempt_num = len(data["attempts"])
        summary_data.append({
            "Model": model_name,
            "Attempt": f"{attempt_num}/{MAX_ATTEMPTS}",
            "Time (s)": f"{latest_result.response_time:.2f}",
            "Status": "Success" if latest_result.error is None else f"{latest_result.error}",
        })
    st.table(summary_data)

    st.subheader("Responses")
    code_language = "python" if language == "Python" else "lean4"

    for model_name, data in st.session_state.results.items():
        latest_result, latest_rid = data["attempts"][-1]
        attempt_num = len(data["attempts"])

        with st.expander(
            f"{model_name} — Attempt {attempt_num}/{MAX_ATTEMPTS} "
            f"({latest_result.response_time:.2f}s) "
            f"{'Success' if latest_result.error is None else 'Error'}"
        ):
            # Show all attempts
            for i, (r, rid) in enumerate(data["attempts"]):
                st.markdown(f"**Attempt {i + 1}:**")
                if r.error:
                    st.error(r.error)
                else:
                    st.code(r.response, language=code_language)

                # Show feedback that was given (if any, for attempts after the first)
                if i < len(data["attempts"]) - 1:
                    st.markdown(f"*Feedback given:* {data['attempts'][i + 1][0].prompt.split('Feedback:')[-1].strip()[:200]}...")
                    st.divider()

            # Feedback input for next attempt
            if attempt_num < MAX_ATTEMPTS and latest_result.error is None:
                feedback = st.text_area(
                    f"Give feedback to {model_name}",
                    key=f"feedback_{model_name}_{attempt_num}",
                    placeholder="e.g., This fails on empty input. Also add type hints.",
                )

                if st.button(f"Send feedback to {model_name}", key=f"btn_{model_name}_{attempt_num}"):
                    if feedback:
                        follow_up_prompt = (
                            f"Here is your previous code:\n\n"
                            f"```\n{latest_result.response}\n```\n\n"
                            f"Feedback: {feedback}\n\n"
                            f"Please fix the code based on this feedback. "
                            f"Return ONLY the corrected code."
                        )

                        with st.spinner(f"Calling {model_name} (attempt {attempt_num + 1})..."):
                            model = get_model(model_name)
                            new_result = model.generate(follow_up_prompt)

                            new_run_id = save_run(
                                model_name=new_result.model_name,
                                task_name=task_name,
                                language=language,
                                prompt_style=style,
                                prompt_text=follow_up_prompt,
                                response=new_result.response,
                                response_time=new_result.response_time,
                                error=new_result.error,
                                parent_run_id=data["parent_run_id"],
                                attempt_number=attempt_num + 1,
                                feedback_given=feedback,
                                input_tokens=new_result.input_tokens,
                                output_tokens=new_result.output_tokens,
                            )

                            data["attempts"].append((new_result, new_run_id))
                            st.rerun()
                    else:
                        st.warning("Please type some feedback first.")
            elif attempt_num >= MAX_ATTEMPTS:
                st.info(f"Maximum {MAX_ATTEMPTS} attempts reached for {model_name}.")