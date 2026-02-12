import streamlit as st
import database
import logic
import time

# Initialize Database
database.init_db()

# Page Configuration
st.set_page_config(page_title="ETL Migration Trainer", layout="wide")

# Sidebar - User Session
st.sidebar.title("👤 User Session")
user_id = st.sidebar.text_input("Enter User ID", "User1")

# Sidebar - AI Configuration
st.sidebar.title("🤖 AI Configuration")
use_ai = st.sidebar.toggle("Use Minimax AI", value=False)
api_key = ""
if use_ai:
    api_key = st.sidebar.text_input("Minimax API Key", type="password")
    if not api_key:
        st.sidebar.warning("Please enter your API Key to use AI features.")

# Sidebar - Pattern Selection
st.sidebar.title("📚 Select Pattern")
pattern_options = list(logic.PATTERNS.keys())
selected_pattern = st.sidebar.selectbox(
    "Choose a Pattern", 
    pattern_options, 
    format_func=lambda x: f"{x} - {logic.PATTERNS[x]}"
)

# Helper function to generate question
def get_new_question(pattern):
    if use_ai and api_key:
        with st.spinner("🤖 AI is generating a question..."):
            return logic.generate_question_with_ai(api_key, pattern)
    else:
        return logic.generate_question(pattern)

# Initialize Session State
if 'current_pattern' not in st.session_state:
    st.session_state['current_pattern'] = selected_pattern

if 'current_question' not in st.session_state:
    q = get_new_question(selected_pattern)
    st.session_state['current_question'] = q
    st.session_state['code_content'] = q # Initialize editor content

# Handle Pattern Change
if st.session_state['current_pattern'] != selected_pattern:
    q = get_new_question(selected_pattern)
    st.session_state['current_question'] = q
    st.session_state['current_pattern'] = selected_pattern
    st.session_state['code_content'] = q
    st.rerun()

# Sidebar - Mistake Notebook
st.sidebar.title("❌ Mistake Notebook")
mistakes = database.get_mistakes(user_id)
if mistakes:
    for m in mistakes:
        # m: id, pattern_type, question_code, user_code, ai_feedback, created_at
        with st.sidebar.expander(f"{m[5]} - {m[1]} (ID: {m[0]})"):
            st.text("Original:")
            st.code(m[2], language='sql')
            st.text("Your Attempt:")
            st.code(m[3], language='sql')
            st.error(m[4])
            if st.button(f"Retry Mistake #{m[0]}", key=f"retry_{m[0]}"):
                st.session_state['current_question'] = m[2]
                st.session_state['current_pattern'] = m[1]
                st.session_state['code_content'] = m[2] # Reset to original question
                st.rerun()
else:
    st.sidebar.info("No mistakes found yet! Keep it up!")

# Main Area
st.title("ETL Migration Training Agent 🚀")

st.markdown(f"### 🎯 Current Task: {logic.PATTERNS[st.session_state['current_pattern']]}")
if use_ai and api_key:
    st.badge("🤖 AI Enabled")
else:
    st.badge("🛠️ Mock Mode")

st.info("💡 Task: Migrate the code below to Snowflake/DataStage standards.")

# Code Editor
code_input = st.text_area("Code Editor", key="code_content", height=200)

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Submit Answer", type="primary"):
        user_code = st.session_state['code_content']
        current_pattern = st.session_state['current_pattern']
        question_code = st.session_state['current_question']
        
        if use_ai and api_key:
            with st.spinner("🤖 AI is reviewing your code..."):
                is_correct, feedback = logic.check_answer_with_ai(api_key, current_pattern, question_code, user_code)
        else:
            is_correct, feedback = logic.check_answer(current_pattern, user_code)
        
        # Save Result
        database.save_training_log(
            user_id=user_id,
            pattern_type=current_pattern,
            question_code=question_code,
            user_code=user_code,
            ai_feedback=feedback,
            is_correct=is_correct
        )

        if is_correct:
            st.success(feedback)
            st.balloons()
        else:
            st.error(feedback)

with col2:
    def on_generate_click():
        q = get_new_question(st.session_state['current_pattern'])
        st.session_state['current_question'] = q
        st.session_state['code_content'] = q
        
    st.button("Generate New Question", on_click=on_generate_click)

st.divider()

# Recent Activity
st.subheader("Recent Activity")
logs = database.get_all_logs(user_id)
if logs:
    for log in logs[:5]:  # Show last 5
        # log: id, pattern_type, question_code, user_code, ai_feedback, is_correct, created_at
        status = "✅ PASS" if log[5] else "❌ FAIL"
        with st.expander(f"[{log[6]}] {log[1]} - {status}"):
             st.text("Question:")
             st.code(log[2], language='sql')
             st.text("Your Code:")
             st.code(log[3], language='sql')
             st.write(f"Feedback: {log[4]}")
