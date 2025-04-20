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
# Rotating topics
available_topics = ["Creating a personalized plan to quit", "Understanding what's in the Quit Kit and how it works", "Making a tapering strategy that fits your life", "Supporting you through cravings, sleep issues, or doubt", "Talking to your partner about quitting", "Handling setbacks without shame", "Finding your motivation again", "Replacing old habits with better ones", "Staying strong when friends are using", "Dealing with morning anxiety", "Navigating social triggers", "Getting back on track after a relapse"]
selected_topics = random.sample(available_topics, 3)
topic_text = "\n".join(f"- {t}" for t in selected_topics)


LOG_FILE = "quit_coach_feedback_log_v1.5.8.csv"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "user_message", "bot_reply", "thumb", "theme"])

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

if "messages" not in st.session_state:
    st.session_state["messages"] = []

    # Load 3 random support topics from external file
    with open("quit_coach_support_topics.txt", "r") as f:
        all_topics = f.read().splitlines()
    selected_topics = random.sample(all_topics, 3)
    formatted_topics = "\n".join(f"- {topic}" for topic in selected_topics)

    # Add assistant greeting
    st.session_state["messages"].append({
        "role": "assistant",
        "content": (
            "Hey there — I’m Quit Coach. I’m here to help you through the toughest parts of quitting, especially the stuff that no one else seems to understand.\n\n"
            "Whether you're feeling stuck, overwhelmed, or just tired of trying to do it alone — I'm here to help.\n\n"
            "Here are a few things I can help with today:\n"
            f"{formatted_topics}\n\n"
            "To get started, can you tell me what substance you’re currently struggling with?"
        )
    })

    st.session_state["craving_stage"] = None

# Display all messages
for i, msg in enumerate(st.session_state["messages"]):
    st.chat_message(msg["role"]).markdown(msg["content"])
    if msg["role"] == "assistant":
        with st.expander("Was this helpful?"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Yes", key=f"yes_{i}"):
                    with open(LOG_FILE, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([datetime.now(), st.session_state.get("last_prompt", ""), msg["content"], "yes", ""])
                    st.success("Thanks for your feedback!")
            with col2:
                if st.button("👎 No", key=f"no_{i}"):
                    with open(LOG_FILE, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([datetime.now(), st.session_state.get("last_prompt", ""), msg["content"], "no", ""])
                    st.warning("Thanks — we'll learn from this.")

# Handle new input
if prompt := st.chat_input("How can I support you today?"):
    st.chat_message("user").markdown(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.session_state["last_prompt"] = prompt

    with st.spinner("Thinking..."):
        try:
            if st.session_state["craving_stage"]:
                stage = st.session_state["craving_stage"]
                if stage == "feedback":
                    if "no" in prompt.lower():
                        st.session_state["craving_stage"] = act_craving_stages["wrapup"]["restart_stage"]
                        reply = act_craving_stages["wrapup"]["prompt_failure"]
                    else:
                        reply = act_craving_stages["wrapup"]["prompt_success"]
                        st.session_state["craving_stage"] = None
                else:
                    st.session_state["craving_stage"] = act_craving_stages[stage]["next"]
                    reply = act_craving_stages[stage]["prompt"]
            elif any(term in prompt.lower() for term in ["craving", "urge", "want to use"]):
                st.session_state["craving_stage"] = "stage_1"
                reply = act_craving_stages["stage_1"]["prompt"]
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state["messages"],
                    temperature=0.8,
                )
                reply = response.choices[0].message["content"].strip() + "\n\nCan you tell me more about that?"
        except Exception as e:
            reply = f"Something went wrong: {str(e)}"

    st.chat_message("assistant").markdown(reply)
    st.session_state["messages"].append({"role": "assistant", "content": reply})