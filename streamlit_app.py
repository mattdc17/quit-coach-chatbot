import streamlit as st
import openai
import random
import csv
import os
from datetime import datetime

from quitkit_ingredients import quitkit_ingredients
from testimonials import testimonials
from kratom_book import kratom_book
from personal_responses import personal_responses
from quitkit_tone_and_rules import tone_and_rules
from quitcoach_behavior_rules import quitcoach_behavior_rules
from quit_coach_support_topics import support_topics

st.set_page_config(page_title="Quit Coach v1.5.8", layout="centered")
st.title("💬 Quit Coach v1.5.8")

openai.api_key = st.secrets.get("OPENAI_API_KEY")

LOG_FILE = "quit_coach_feedback_log_v1.5.8.csv"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "user_message", "bot_reply", "thumb", "theme"])

if "messages" not in st.session_state:
    selected_testimonials = "\n".join(random.sample(testimonials, 3))
    selected_topics = random.sample(support_topics, 3)
    topics_display = "\n".join(f"- {t}" for t in selected_topics)

    system_prompt = """
You are Quit Coach, a grounded, hopeful recovery assistant built by the creator of the Quit Kit.

TONE:
Sound like a grounded recovery coach. Supportive, CBT-influenced, and hopeful. Promote the Quit Kit gently but consistently.

RULES:
Build rapport before giving suggestions. Ask about struggles, triggers, and past attempts. Never give general lists. Always personalize.

TESTIMONIAL:
"This kit helped me more in 3 weeks than anything else in 3 years of struggling. I finally feel like myself again."

INGREDIENTS OVERVIEW:
The Quit Kit includes 3 daily doses with neurotransmitter support, energy/mood stabilizers, adaptogens, and sleep aids.

KRATOM BOOK INSIGHTS:
The Kratom Book teaches that addiction recovery is about structure, compassion, and consistency. It highlights ACT-based craving tools, values-focused decisions, and letting go of shame.

RESPONDING STYLE:
Use a grounded, real-talk tone. Reflect empathy, acknowledge struggle, and guide gently toward insight or action—never judgment.

Your job is to guide the user through the process of quitting by creating a personalized plan. Start by learning about the person’s substance use, goals, pain points, and fears. Stay connected, supportive, and practical. Offer suggestions only after getting a clear picture of who they are and what they’re struggling with.
"""


    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]
    st.session_state["last_prompt"] = ""
    st.session_state["last_reply"] = ""

    st.session_state["messages"].append({
        "role": "assistant",
        "content": (
            "Hey — I’m Quit Coach. I’m here to help you build a real plan to quit — not just talk about it.\n\n"
            "We’ll start by understanding where you're at, what you're struggling with, and what kind of support you need.\n\n"
            "Here are a few things I can help with today:\n"
            f"{topics_display}\n\n"
            "To begin, what substance are you currently struggling with?"
        )
    })

# Display message history
for i, msg in enumerate(st.session_state["messages"]):
    if msg["role"] != "system":
        st.chat_message(msg["role"]).markdown(msg["content"])
        if msg["role"] == "assistant" and i == len(st.session_state["messages"]) - 1:
            with st.expander("Was this helpful?"):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍 Yes", key=f"yes_{i}"):
                        with open(LOG_FILE, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow([datetime.now(), st.session_state["last_prompt"], st.session_state["last_reply"], "yes", ""])
                        st.success("Thanks for your feedback!")
                with col2:
                    if st.button("👎 No", key=f"no_{i}"):
                        with open(LOG_FILE, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow([datetime.now(), st.session_state["last_prompt"], st.session_state["last_reply"], "no", ""])
                        st.warning("Thanks — we'll keep improving.")

# Handle new input
if prompt := st.chat_input("How can I support you today?"):
    st.chat_message("user").markdown(prompt)
    st.session_state["last_prompt"] = prompt
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state["messages"],
                temperature=0.8,
            )
            reply = response.choices[0].message["content"].strip()
        except Exception as e:
            reply = f"Something went wrong: {str(e)}"

    st.session_state["last_reply"] = reply
    st.chat_message("assistant").markdown(reply)
    st.session_state["messages"].append({"role": "assistant", "content": reply})
