# Initialize user_plan tracker to build structured quit plan
import streamlit as st
if "user_plan" not in st.session_state:
    st.session_state["user_plan"] = {}

# Helper function to update plan entries
def update_user_plan(section, content):
    st.session_state["user_plan"][section] = content

# Helper to download quit plan as TXT file
def generate_quit_plan_txt():
    from io import StringIO
    buffer = StringIO()
    buffer.write("YOUR PERSONAL QUIT PLAN\n")
    buffer.write("========================\n\n")
    for section, content in st.session_state["user_plan"].items():
        title = section.replace("_", " ").title()
        buffer.write(f"{title}:\n{content}\n\n")
    buffer.seek(0)
    return buffer