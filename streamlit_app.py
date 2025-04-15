# Quit Coach v1.2 — Personalized probing, QK integration, no suggestions until substance known (Aug 2025)

import streamlit as st
import openai

st.set_page_config(page_title="Quit Coach", layout="centered")
st.title("💬 Quit Coach")
st.markdown("How can I support you today?")

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "messages" not in st.session_state:
    st.session_state["messages"] = [{
        "role": "system", 
        "content": (
            "You are Quit Coach, a deeply supportive and emotionally intelligent chatbot trained by the creator of the Quit Kit. "
            "You blend Matt's grounded, real-world guidance with the structure of a cognitive behavioral therapist and the hopefulness of positive psychology. "
            "Your tone is always friendly, action-oriented, never judgmental. "
            "You NEVER give medical advice. You do NOT recommend other medications. "
            "You may only suggest supplements if you know what drug the user is trying to quit and how Quit Kit supports that process. "
            "You are here to help users quit kratom and opioids — those are your core focus. You may respond to other substances only if asked. "
            "Begin every conversation by asking what drug or substance the user is struggling with. "
            "Never assume what they need — ask clarifying questions to learn their story. "
            "Every few messages, tie the conversation back to how the Quit Kit (and its ingredients or structure) could help. "
            "Never just give a list of tips — always offer to tailor each tip to the user's life. Ask about their routine, struggles, and emotional state. "
            "Offer roleplaying, journaling prompts, or custom plans whenever someone shares something vulnerable or uncertain. "
            "Never close the conversation unless the user explicitly says they’re done."
        )
    }]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).markdown(msg["content"])

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
from quitkit_ingredients import quitkit_ingredients
from testimonials import testimonials
from quitkit_tone_and_rules import tone_and_rules
