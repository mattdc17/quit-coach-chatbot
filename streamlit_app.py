# Quit Coach v1.5.1 — Logs feedback and auto-tags themes (Apr 2025)

import streamlit as st
import openai
import random
import csv
import os
from datetime import datetime

from quitkit_ingredients import quitkit_ingredients
from testimonials import testimonials
from quitkit_tone_and_rules import tone_and_rules

st.set_page_config(page_title="Quit Coach", layout="centered")
st.title("💬 Quit Coach")
st.caption("Quit Coach v1.5.1 — Feedback & theme tracking enabled")

openai.api_key = st.secrets["OPENAI_API_KEY"]

# CSV file to store feedback
LOG_FILE = "quit_coach_feedback_log.csv"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "user_message", "bot_reply", "thumb", "theme"])

def detect_theme(text):
    text = text.lower()
    if "craving" in text or "urge" in text:
        return "cravings"
    elif "taper" in text or "cut down" in text:
        return "tapering"
    elif "sleep" in text or "insomnia" in text:
        return "sleep"
    elif "relapse" in text or "fail" in text:
        return "guilt/shame"
    elif "motivation" in text or "why quit" in text:
        return "motivation"
    elif "ingredient" in text or "what's in" in text:
        return "quit kit info"
    else:
        return "other"

# Quit Kit overview
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

# Initialize system prompt and welcome message
if "messages" not in st.session_state:
    selected_testimonials = "\n".join(random.sample(testimonials, 3))
    system_prompt = f"""
You are Quit Coach, a supportive, grounded chatbot trained by the creator of the Quit Kit.
You focus on kratom and opioid withdrawal. You blend grounded encouragement with CBT structure and positive psychology.

Here are your tone and behavior rules:
{tone_and_rules}

Here is the Quit Kit daily schedule and purpose:
{quitkit_overview}

Here is the verified ingredient list by dose:
{quitkit_ingredients}

Here are real, unedited testimonials:
{selected_testimonials}

Never ask the user if they’ve heard of the Quit Kit — assume they know.
Only reference ingredients found in the quitkit_ingredients.py file.
If unsure about an ingredient, say so clearly.
Start every conversation by asking what drug the user is trying to quit.
Always follow advice with a concrete, real-life example.
Offer a plan or action the user could take today.
Keep the conversation going until the user says they’re done.
Mention the Quit Kit within the first few responses and relate its structure or ingredients back to the user’s pain points regularly.
"""
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]
    st.session_state["last_prompt"] = ""
    st.session_state["last_reply"] = ""

    st.session_state["messages"].append({
        "role": "assistant",
        "content": (
    "Hey there — I’m Quit Coach, here to support you every step of the way.\n\n"
    "Here are a few things I can help with:\n"
    "- Creating a personalized plan to quit\n"
    "- Understanding what's in the Quit Kit and how it works\n"
    "- Making a tapering strategy that fits your life\n"
    "- Supporting you through cravings, sleep issues, or doubt\n\n"
    "To get started, can you tell me what substance you're trying to quit?"
)

    })

# Show chat messages
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] != "system":
        st.chat_message(msg["role"]).markdown(msg["content"])
        if msg["role"] == "assistant" and i == len(st.session_state.messages) - 1:
            with st.expander("Was this helpful?"):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍 Yes", key=f"yes_{i}"):
                        with open(LOG_FILE, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow([datetime.now(), st.session_state["last_prompt"], st.session_state["last_reply"], "yes", detect_theme(st.session_state["last_prompt"])])
                        st.success("Thanks for your feedback!")
                with col2:
                    if st.button("👎 No", key=f"no_{i}"):
                        with open(LOG_FILE, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow([datetime.now(), st.session_state["last_prompt"], st.session_state["last_reply"], "no", detect_theme(st.session_state["last_prompt"])])
                        st.warning("Thanks — we’ll learn from this.")

# Handle new user prompt
if prompt := st.chat_input("How can I support you today?"):
    st.chat_message("user").markdown(prompt)
    st.session_state["last_prompt"] = prompt
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

    st.session_state["last_reply"] = reply
    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})