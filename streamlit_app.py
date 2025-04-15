# Quit Coach v1.3 — Full integration with Quit Kit ingredients, testimonials, and tone logic (Aug 2025)

import streamlit as st
import openai
import random

from quitkit_ingredients import quitkit_ingredients
from testimonials import testimonials
from quitkit_tone_and_rules import tone_and_rules

st.set_page_config(page_title="Quit Coach", layout="centered")
st.title("💬 Quit Coach")
st.caption("Quit Coach v1.3 — Last updated August 2025")

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "messages" not in st.session_state:
    system_prompt = (
        "You are Quit Coach, a supportive, grounded chatbot trained by the creator of the Quit Kit. "
        f"Your primary focus is supporting people quitting kratom or opioids. "
        f"You blend Matt's direct support style with CBT and positive psychology. "
        f"Here are your tone and behavior rules: {tone_and_rules}\n"
        f"Here are the Quit Kit ingredients: {quitkit_ingredients}\n"
        f"Here are some real testimonials to help reflect your tone: {random.sample(testimonials, 3)}\n"
        "Start every conversation by asking what drug or substance the user is trying to quit. "
        "Never make supplement suggestions until the user's substance is clear. "
        "Always ask follow-up questions, never end the conversation, and offer custom plans based on the user's needs."
    )
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).markdown(msg["content"])

# Chat input
if prompt := st.chat_input("What’s on your mind?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages,
                temperature=0.85,
            )
            reply = response.choices[0].message["content"]
        except Exception as e:
            reply = f"Something went wrong: {e}"

    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})