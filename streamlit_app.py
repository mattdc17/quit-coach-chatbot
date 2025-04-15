# Quit Coach v1.4.1 — Strict ingredient enforcement, session cache reset reminder (Apr 2025)

import streamlit as st
import openai
import random

from quitkit_ingredients import quitkit_ingredients
from testimonials import testimonials
from quitkit_tone_and_rules import tone_and_rules

st.set_page_config(page_title="Quit Coach", layout="centered")
st.title("💬 Quit Coach")
st.caption("Quit Coach v1.4.1 — Last updated April 2025")

openai.api_key = st.secrets["OPENAI_API_KEY"]

# Hardcoded overview of schedule and purpose
quitkit_overview = """
Quit Kit is a targeted, three-dose daily supplement regimen designed to support individuals transitioning away from kratom and opioid dependence.

It helps restore balance to the brain and body by:
- Replenishing neurotransmitters
- Reducing cravings
- Stabilizing mood
- Promoting restorative sleep

Dosing schedule:
- Morning Dose: Upon waking — energy, cognition, mood
- Afternoon Dose: 5–6 hours later — stress, cravings, neurotransmitter support
- Nighttime Dose: 30–60 minutes before bed — relaxation and sleep
"""

# Initialize new session (clearing cache if needed)
if st.button("🔄 Reset Conversation"):
    st.session_state.clear()

if "messages" not in st.session_state:
    selected_testimonials = "\n".join(random.sample(testimonials, 3))
    system_prompt = (
        "You are Quit Coach, a supportive, grounded chatbot trained by the creator of the Quit Kit. "
        "You focus on kratom and opioid withdrawal. You blend grounded encouragement with CBT structure and positive psychology.\n\n"
        f"Here are your tone and behavior rules: {tone_and_rules}\n\n"
        f"Here is the Quit Kit daily schedule and purpose: {quitkit_overview}\n\n"
        f"Here is the verified ingredient list by dose: {quitkit_ingredients}\n\n"
        f"Here are real, unedited testimonials: {selected_testimonials}\n\n"
        "Only reference ingredients found in the quitkit_ingredients.py file. Do not infer or add any other substances. "
        "If you are unsure whether something is included, say so clearly. "
        "Start every conversation by asking what drug the user is trying to quit. "
        "When asked about ingredients, offer a deep dive into their science. "
        "Refer to the Quit Kit’s three-dose schedule when users ask how to take it. "
        "Do not close the conversation unless the user says so."
    )
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]

# Display prior conversation
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).markdown(msg["content"])

# Chat input field
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