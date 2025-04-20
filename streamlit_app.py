import streamlit as st
import openai
import random
import csv
import os
from datetime import datetime
from quitkit_ingredients import quitkit_ingredients
from testimonials import testimonials

st.set_page_config(page_title="Quit Coach v1.5.8", layout="centered")
st.title("💬 Quit Coach v1.5.8")

openai.api_key = st.secrets.get("OPENAI_API_KEY")

# CSV file to store feedback
LOG_FILE = "quit_coach_feedback_log_v1.5.8.csv"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "user_message", "bot_reply", "thumb", "theme"])

# ACT craving stage map
act_craving_stages = {
    "stage_1": {
        "prompt": "Thanks for sharing that — it makes sense that certain situations bring up cravings. Let’s walk through this together. I’ll guide you step-by-step through a craving support method that helps reduce the pull — not by fighting it, but by making space around it. You with me?",
        "next": "stage_2"
    },
    "stage_2": {
        "prompt": "Let’s get grounded for a second. What’s one thing you can see, one thing you can hear, and one thing you can physically feel right now?",
        "next": "stage_3"
    },
    "stage_3": {
        "prompt": "Good. Now, when that craving hits, what thought goes through your mind? Try saying, 'I’m having the thought that…' and fill in the rest.",
        "next": "stage_4"
    },
    "stage_4": {
        "prompt": "Rather than trying to get rid of the craving, let’s try something different. Where do you feel that urge in your body? Is it tension, restlessness, something else?",
        "next": "stage_5"
    },
    "stage_5": {
        "prompt": "You’re not your craving — you’re the one watching it. Imagine looking down on this moment from a satellite view. What do you notice?",
        "next": "stage_6"
    },
    "stage_6": {
        "prompt": "Let’s get clear on what you’re doing this for. What do you want more than that short-term relief? Who or what are you quitting for?",
        "next": "stage_7"
    },
    "stage_7": {
        "prompt": "Now — what’s one small thing you can do next time a craving hits? Something real: maybe a phrase you’ll say out loud, someone you'll text, or a Quit Kit dose.",
        "next": "feedback"
    },
    "feedback": {
        "prompt": "You didn’t fight the craving — you walked through it. That’s powerful. Did this help you get through the craving?",
        "next": "wrapup"
    },
    "wrapup": {
        "prompt_success": "I’m proud of you. Every time you walk through a craving like this, you build strength. Want to save this plan for next time?",
        "prompt_failure": "Totally fair. Let’s circle back to grounding. What’s one thing in the room right now that you hadn’t noticed before?",
        "restart_stage": "stage_2"
    }
}

# Behavior and opening messages
behavior_rules = '''...'''  # Truncated for brevity
quitkit_overview = '''...'''  # Truncated for brevity

if "messages" not in st.session_state:
    selected_testimonials = "\n".join(random.sample(testimonials, 3))
    system_prompt = f"..."
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

# Display messages
for i, msg in enumerate(st.session_state["messages"]):
    if msg["role"] != "system":
        st.chat_message(msg["role"]).markdown(msg["content"])

# Craving interaction logic
if "craving_stage" in st.session_state:
    user_input = st.chat_input("How are you feeling right now?")
    if user_input:
        st.chat_message("user").markdown(user_input)
        stage = st.session_state["craving_stage"]
        if stage == "feedback":
            if "no" in user_input.lower():
                st.session_state["craving_stage"] = act_craving_stages["wrapup"]["restart_stage"]
                reply = act_craving_stages["wrapup"]["prompt_failure"]
            else:
                reply = act_craving_stages["wrapup"]["prompt_success"]
                del st.session_state["craving_stage"]
        else:
            st.session_state["craving_stage"] = act_craving_stages[stage]["next"]
            reply = act_craving_stages[stage]["prompt"]
        st.chat_message("assistant").markdown(reply)
else:
    prompt = st.chat_input("How can I support you today?")
    if prompt:
        st.chat_message("user").markdown(prompt)
        if any(term in prompt.lower() for term in ["craving", "urge", "want to use"]):
            st.session_state["craving_stage"] = "stage_1"
            reply = act_craving_stages["stage_1"]["prompt"]
        else:
            reply = "Got it — let's build a plan around that. What’s been the hardest part of quitting so far?"
        st.chat_message("assistant").markdown(reply)