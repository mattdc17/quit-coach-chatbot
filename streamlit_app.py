import streamlit as st
import openai

st.set_page_config(page_title="Quit Coach", layout="centered")

st.title("💬 Quit Coach")
st.markdown("Quit Coach is here to support you through cravings, doubt, sleep issues, and everything in between.")

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": (
        "You are Quit Coach, a supportive, grounded, and encouraging chatbot trained by the creator of the Quit Kit. "
        "You never give medical advice. You do not recommend other medications or untested regimens. "
        "You are here to provide motivation, ingredient insights, and practical guidance to people quitting kratom or alcohol. "
        "Your tone is always friendly, hopeful, and action-oriented — never judgmental or robotic."
    )}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

if prompt := st.chat_input("How can I support you today?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Thinking..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=st.session_state.messages,
                temperature=0.8,
            )
            reply = response.choices[0].message["content"]
        except Exception as e:
            reply = f"Something went wrong: {e}"
    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})