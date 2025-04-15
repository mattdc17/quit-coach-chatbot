# Quit Coach v1.4.3 — Assumes Quit Kit awareness, concrete examples added (Apr 2025)

import streamlit as st
import openai
import random

from quitkit_ingredients import quitkit_ingredients
from testimonials import testimonials
from quitkit_tone_and_rules import tone_and_rules

st.set_page_config(page_title="Quit Coach", layout="centered")
st.title("💬 Quit Coach")
st.caption("Quit Coach v1.4.3 — Last updated April 2025")

openai.api_key = st.secrets["OPENAI_API_KEY"]

# Overview message with Quit Kit structure
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

# Initialize the assistant logic
if "messages" not in st.session_state:
    selected_testimonials = "\n".join(random.sample(testimonials, 3))
    system_prompt = (
        "You are Quit Coach, a supportive, grounded chatbot trained by the creator of the Quit Kit. "
        "You focus on kratom and opioid withdrawal. You blend grounded encouragement with CBT structure and positive psychology.\n\n"
        f"Here are your tone and behavior rules: {tone_and_rules}\n\n"
        f"Here is the Quit Kit daily schedule and purpose: {quitkit_overview}\n\n"
        f"Here is the verified ingredient list by dose: {quitkit_ingredients}\n\n"
        f"Here are real, unedited testimonials: {selected_testimonials}\n\n"
        "Never ask the user if they’ve heard of the Quit Kit — assume they know. "
        "Only reference ingredients found in the quitkit_ingredients.py file. "
        "If unsure about an ingredient, say so clearly. "
        "Start every conversation by asking what drug the user is trying to quit. "
        "Always follow advice with a concrete, real-life example. "
        "Offer a plan or action the user could take today. "
        "Keep the conversation going until the user says they’re done. "
        "Mention the Quit Kit within the first few responses and relate its structure or ingredients back to the user’s pain points regularly."
    )
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]

    # Initial assistant message with helpful suggestions
    st.session_state["messages"].append({
        "role": "assistant",
        "content": '''Hey there — I’m Quit Coach, here to support you every step of the way.

Here are a few things I can help with:
- Creating a personalized plan to quit
- Understanding what's in the Quit Kit and how it works
- Making a tapering strategy that fits your life
- Supporting you through cravings, sleep issues, or doubt

To get started, can you tell me what substance you're trying to quit?'''

       })
    

# Display conversation history
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).markdown(msg["content"])

# Chat input field
if prompt := st.chat_input("How can I support you today?"):
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