import streamlit as st
from quitcoach_plan_writer import generate_quit_plan_txt  # Update path as needed

def show_download_button():
    if st.session_state.get("final_quit_plan"):
        file_content = generate_quit_plan_txt(st.session_state["final_quit_plan"])
        st.download_button(
            label="📄 Download My Quit Plan",
            data=file_content,
            file_name="my_quit_plan.txt",
            mime="text/plain"
        )
