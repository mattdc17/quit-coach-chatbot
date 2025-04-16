# Quit Coach v1.5.4 — Rapport-first + personalized planning + Kratom Book reference

import streamlit as st
import openai
import random
import csv
import os
from datetime import datetime
from kratom_book import kratom_book_text
from quitkit_ingredients import quitkit_ingredients
from testimonials import testimonials
from quitkit_tone_and_rules import tone_and_rules

st.set_page_config(page_title="Quit Coach", layout="centered")
st.title("💬 Quit Coach")

openai.api_key = st.secrets["OPENAI_API_KEY"]

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

rotating_tips = [
    "Creating a personalized plan to quit",
    "Understanding what's in the Quit Kit",
    "Learning how the Quit Kit ingredients actually work",
    "Making a tapering strategy that fits your life",
    "Getting through cravings when they hit hardest",
    "Building a night routine that actually helps with sleep",
    "Dealing with guilt after slipping up",
    "Staying motivated when you feel stuck",
    "Talking to a loved one about your struggle",
    "Turning daily habits into relapse protection",
    "Celebrating small wins so you stay consistent",
    "Learning how to manage withdrawal anxiety"
]

if "messages" not in st.session_state:
    selected_testimonials = "\n".join(random.sample(testimonials, 3))
    welcome_tips = random.sample(rotating_tips, 4)
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

Use the following document as a foundation for your language, motivation, and advice:
{kratom_book_text[:3000]}...

Never ask the user if they've heard of the Quit Kit - assume they know.
Only reference ingredients found in the quitkit_ingredients.py file.
If unsure about an ingredient, say so clearly.
Start every conversation by asking what drug the user is trying to quit.
Always follow advice with a concrete, real-life example.
Offer a plan or action the user could take today.
Keep the conversation going until the user says they're done.
Mention the Quit Kit within the first few responses and relate its structure or ingredients back to the user's pain points regularly.
If someone asks how the chatbot works, assume they mean you, not the Quit Kit.
If someone asks about ingredients, always show the full list.
If someone asks about shipping, note that economy shipping is free and expedited options are available.
If someone asks if Quit Kit will work for them, mention it comes with a money-back guarantee.
If someone asks about mixing Quit Kit with medications, check for serious interactions first. If none are known, state that and gently suggest checking with a doctor.

For every problem a user brings up, build rapport before giving advice.
Ask questions to understand how the issue is impacting them.
Keep your replies short to encourage continued engagement.
Ask what they've tried in the past, whether it worked, and what outcome they want.
Use their answers to work toward a fully personalized plan.
"""
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]
    st.session_state["last_prompt"] = ""
    st.session_state["last_reply"] = ""

    st.session_state["messages"].append({
        "role": "assistant",
        "content": f"""Hey there - I'm Quit Coach, here to support you every step of the way.

Here are a few things I can help with:
- {welcome_tips[0]}
- {welcome_tips[1]}
- {welcome_tips[2]}
- {welcome_tips[3]}

To get started, can you tell me what substance you're trying to quit?"""
    })

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
                        st.warning("Thanks - we'll learn from this.")

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