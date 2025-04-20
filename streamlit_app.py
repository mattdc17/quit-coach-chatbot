
import streamlit as st
import openai
import random
import csv
import os
from datetime import datetime

from kratom_book import kratom_book
from personal_responses import personal_responses
from quitkit_ingredients import quitkit_ingredients
from testimonials import testimonials
from quitkit_tone_and_rules import quitkit_tone_and_rules
from quitcoach_behavior_rules import behavior_rules

st.set_page_config(page_title="Quit Coach v1.5.8", layout="centered")
st.title("💬 Quit Coach v1.5.8")

openai.api_key = st.secrets.get("OPENAI_API_KEY")

# CSV file to store feedback
LOG_FILE = "quit_coach_feedback_log_v1.5.8.csv"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "user_message", "bot_reply", "thumb", "theme"])

# Support topics
with open("quit_coach_support_topics.txt") as f:
    all_topics = [line.strip() for line in f.readlines() if line.strip()]

# Compose system prompt
system_prompt = f"""
You are Quit Coach, a supportive, grounded chatbot trained by the creator of the Quit Kit.

{behavior_rules}

{quitkit_tone_and_rules}

Here is the verified ingredient list by dose in full:
{quitkit_ingredients}

Here are real, unedited testimonials:
{testimonials}

Here are personal emotional support responses:
{personal_responses}

Here are longform insights from the creator's own journey:
{kratom_book}

Always begin by asking about the user's specific experience before offering any advice or planning.
"""

# Load support intro topics
intro_topics = random.sample(all_topics, 3)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]
    st.session_state["last_prompt"] = ""
    st.session_state["last_reply"] = ""
    st.session_state["messages"].append({
        "role": "assistant",
        "content": (
            "Hey there — I’m Quit Coach. I’m here to help you through the toughest parts of quitting, "
            "especially the stuff that no one else seems to understand.

"
            "Whether you're feeling stuck, overwhelmed, or just tired of trying to do it alone — I'm here to help.

"
            "Here are a few things I can help with today:
"
            f"- {intro_topics[0]}
- {intro_topics[1]}
- {intro_topics[2]}

"
            "To get started, can you tell me what substance you’re currently struggling with?"
        )
    })

# Display messages
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
                        st.warning("Thanks — we'll learn from this.")

# Craving protocol logic
if "craving_stage" in st.session_state:
    stage = st.session_state["craving_stage"]
    user_input = st.session_state["last_prompt"].lower()

    if stage == "stage_1":
        st.session_state["craving_trigger"] = user_input
        st.session_state["craving_stage"] = "stage_2"
        reply = (
            "Thanks for sharing that. Let’s ground ourselves for a moment. "
            "What’s one thing you can see, one thing you can hear, and one thing you can physically feel right now?"
        )

    elif stage == "stage_2":
        st.session_state["craving_grounding"] = user_input
        st.session_state["craving_stage"] = "stage_3"
        reply = (
            "Great. Now notice what thought is riding alongside this craving. "
            "Try silently saying, 'I'm having the thought that…' and finish the sentence. What thought came up?"
        )

    elif stage == "stage_3":
        st.session_state["craving_defusion"] = user_input
        st.session_state["craving_stage"] = "stage_4"
        reply = (
            "You’re doing really well. Now let’s open up to the craving instead of fighting it. "
            "Where do you feel it in your body?"
        )

    elif stage == "stage_4":
        st.session_state["craving_acceptance"] = user_input
        st.session_state["craving_stage"] = "stage_5"
        reply = (
            "Now let’s connect to what matters to you. "
            "What are you doing this for? Who or what is on the other side of this quit that makes it worth it?"
        )

    elif stage == "stage_5":
        st.session_state["craving_values"] = user_input
        st.session_state["craving_stage"] = "stage_6"
        reply = (
            "Awesome. Let’s take action now. Maybe it's time for your Quit Kit dose, a cold drink, or a walk. "
            "What small action can you take right now to carry this momentum forward?"
        )

    elif stage == "stage_6":
        st.session_state["craving_action"] = user_input
        st.session_state["craving_stage"] = "feedback"
        reply = (
            "You just walked through that craving — breath by breath. That’s the kind of progress that sticks. "
            "Did this help you get through it?"
        )

    elif stage == "feedback":
        if "no" in user_input:
            st.session_state["craving_stage"] = "stage_2"
            reply = (
                "Totally fair. Let's go again — we'll use a different grounding strategy this time. "
                "Look around and name something in the room you’ve never noticed before."
            )
        else:
            del st.session_state["craving_stage"]
            reply = (
                "I’m proud of you. You didn’t run from the craving — you walked through it. "
                "Each time you do that, you build strength."
            )

elif prompt := st.chat_input("How can I support you today?"):
    st.chat_message("user").markdown(prompt)
    st.session_state["last_prompt"] = prompt
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
        try:
            if any(word in prompt.lower() for word in ["craving", "urge", "want to use"]):
                st.session_state["craving_stage"] = "stage_1"
                reply = (
                    "Cravings can be intense — but they don’t have to control you. "
                    "Can you tell me when your cravings usually happen?"
                )
            else:
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
