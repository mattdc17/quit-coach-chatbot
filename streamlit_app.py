import streamlit as st
import openai
import random
import csv
import os
from datetime import datetime
from io import StringIO

from kratom_book import kratom_book
from personal_responses import personal_responses
from quitkit_ingredients import quitkit_ingredients
from testimonials import testimonials
from quitkit_tone_and_rules import quitkit_tone_and_rules
from quitcoach_behavior_rules import behavior_rules

st.set_page_config(page_title="Quit Coach v1.6", layout="centered")
st.title("💬 Quit Coach v1.6")

openai.api_key = st.secrets.get("OPENAI_API_KEY")

# --- Plan Tracker ---
if "user_plan" not in st.session_state:
    st.session_state["user_plan"] = {}

def update_user_plan(section, content):
    st.session_state["user_plan"][section] = content

def generate_quit_plan_txt():
    buffer = StringIO()
    buffer.write("YOUR PERSONAL QUIT PLAN\n")
    buffer.write("========================\n\n")
    for section, content in st.session_state["user_plan"].items():
        title = section.replace("_", " ").title()
        buffer.write(f"{title}:\n{content}\n\n")
    buffer.seek(0)
    return buffer

# --- System Prompt ---
if "messages" not in st.session_state:
    selected_testimonials = "\n".join(random.sample(testimonials, 3))
    system_prompt = f"""
You are Quit Coach, a supportive, grounded chatbot trained by the creator of the Quit Kit.

Your mission is to help each user build a personal plan to quit — one step at a time.
You are not here to dump advice. You are here to guide, reflect, and co-create a real, structured plan they can walk away with and follow.

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

Always begin by asking about the user’s specific experience before offering any advice or planning.
"""
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]
    st.session_state["last_prompt"] = ""
    st.session_state["last_reply"] = ""
    st.session_state["messages"].append({
        "role": "assistant",
        "content": (
            "Hey — I’m Quit Coach. I’m not just here to chat — I’m here to help you build a personal plan to quit. "
            "A real one. One that fits your life, your struggle, and your goals.\n\n"
            "You and I are going to talk it through, one step at a time. No pressure. No judgment. "
            "Just support, questions that matter, and a plan that’s yours when you're ready.\n\n"
            "To start, can you tell me what substance you're trying to quit?"
        )
    })

# --- Display Chat History ---
for i, msg in enumerate(st.session_state["messages"]):
    if msg["role"] != "system":
        st.chat_message(msg["role"]).markdown(msg["content"])

# --- Chat Input ---
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

# --- Plan Download Button ---
if st.session_state.get("user_plan") and len(st.session_state["user_plan"]) >= 3:
    st.markdown("### 📋 Want to take your plan with you?")
    plan_buffer = generate_quit_plan_txt()
    st.download_button(
        label="⬇️ Download My Quit Plan",
        data=plan_buffer,
        file_name="my_quit_plan.txt",
        mime="text/plain"
    )