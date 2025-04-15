# Quit Coach v1.4 — Strict ingredient reference, deep dive option, QK structure included (Aug 2025)

import streamlit as st
import openai
import random

from quitkit_ingredients import quitkit_ingredients
from testimonials import testimonials
from quitkit_tone_and_rules import tone_and_rules

st.set_page_config(page_title="Quit Coach", layout="centered")
st.title("💬 Quit Coach")
st.caption("Quit Coach v1.4 — Last updated August 2025")

openai.api_key = st.secrets["OPENAI_API_KEY"]

# Structured overview of Quit Kit function and schedule
quitkit_overview = (
    "Quit Kit is a targeted, three-dose daily supplement regimen designed to support individuals transitioning away from kratom and opioid dependence. "
    "Formulated with 12 clinically studied, non-prescription compounds, it helps restore balance to the brain and body during withdrawal by replenishing key neurotransmitters, reducing cravings, stabilizing mood, and promoting restorative sleep. "
    "The Quit Kit consists of three daily doses, each taken as a 3-capsule serving:

"
    "- Morning Dose: Taken upon waking, supports cognitive function and energy.
"
    "- Afternoon Dose: Taken 5–6 hours after the morning dose, helps manage stress and neurotransmitter balance.
"
    "- Nighttime Dose: Taken 30–60 minutes before bed, aids in relaxation and sleep quality.
"
)

# Initialize chat session
if "messages" not in st.session_state:
    selected_testimonials = "\n".join(random.sample(testimonials, 3))
    system_prompt = (
        "You are Quit Coach, a supportive, grounded chatbot trained by the creator of the Quit Kit. "
        "You focus on kratom and opioid withdrawal. You blend grounded encouragement with CBT structure and positive psychology.\n\n"
        f"Here are your tone and behavior rules: {tone_and_rules}\n\n"
        f"Here is the Quit Kit daily structure and science: {quitkit_overview}\n\n"
        f"Here is the verified ingredient list by dose: {quitkit_ingredients}\n\n"
        f"Here are real, unedited testimonials: {selected_testimonials}\n\n"
        "Start every conversation by asking what drug or substance the user is trying to quit. Do not offer advice until this is known. "
        "Do not reference any ingredients not found in the uploaded list. "
        "Always follow suggestions with a deeper question or offer to personalize. "
        "Mention the Quit Kit naturally within the first few responses, and bring it back every few messages when relevant. "
        "If the user asks about the Quit Kit ingredients, offer to give a scientific deep dive into how they help with withdrawal."
    )
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]

# Display conversation history
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