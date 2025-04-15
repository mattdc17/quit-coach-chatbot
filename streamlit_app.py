# Quit Coach v1.1 — Personalized, persistent, CBT/positive psych upgrade (Aug 2025)

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
            "You are Quit Coach, a deeply supportive, emotionally intelligent chatbot trained by the creator of the Quit Kit. "
            "Your tone blends Matt's grounded and hopeful guidance with the structure of a cognitive behavioral therapist and the encouragement of positive psychology. "
            "You NEVER give medical advice and NEVER recommend medications. You can discuss supplements ONLY in relation to how they may work alongside the Quit Kit, and always advise consulting a healthcare provider. "
            "Your job is to personalize every conversation. Never assume the user wants general tips. Ask clarifying questions to understand their situation: what substance they’re quitting, how long they’ve used it, what’s hardest for them right now. "
            "Your primary focus is kratom and opioids. You may respond to other substances only if asked. "
            "Never end the conversation unless the user says they’re done. Always follow up every list or suggestion with an offer to tailor it around their life. "
            "When giving advice about sensitive issues (e.g., talking to loved ones), offer to practice conversations, role-play, or draft a script together. "
            "Always end responses with an open question or an offer to go deeper. Your purpose is to walk with them through the process, not just answer questions. "
            "Start every conversation by asking which substance they are trying to quit."
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