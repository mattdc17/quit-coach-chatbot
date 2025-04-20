import streamlit as st
import openai
import random
import csv
import os
from datetime import datetime
from docx import Document

from quitkit_ingredients import quitkit_ingredients
from testimonials import testimonials

st.set_page_config(page_title="Quit Coach v1.5.8", layout="centered")
st.title("💬 Quit Coach v1.5.8")

openai.api_key = st.secrets.get("OPENAI_API_KEY")

# Load ACT Craving Guide from Word doc
def load_act_craving_guide():
    doc = Document("QuitCoach_ACT_Craving_Guide_v2.docx")
    content = []
    for para in doc.paragraphs:
        if para.text.strip():
            content.append(para.text.strip())
    return "\n\n".join(content)

act_craving_reference = load_act_craving_guide()

# CSV file to store feedback
LOG_FILE = "quit_coach_feedback_log_v1.5.8.csv"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "user_message", "bot_reply", "thumb", "theme"])

# Behavior rules override system-wide
behavior_rules = '''
Behavior Rules:
1. ALWAYS list the full ingredient breakdown when a user asks:
   - "What's in the Quit Kit?"
   - "What's in the morning dose?", "What's in the afternoon dose?", "What's in the nighttime dose?"
   -> Pull full lists from quitkit_ingredients.py and show the full breakdown without summarizing.

2. NEVER offer suggestions or plans until you've built rapport.
   - Ask about the user's specific experiences (e.g., cravings, sleep, motivation).
   - Learn when it happens, how it affects them, what they've tried.
   - Offer suggestions ONLY after getting a personal, user-specific picture.

3. ALWAYS bring up the Quit Kit at least once every 3 messages, preferably by connecting an ingredient or its effect to the user's concern.

4. Do not offer a list of suggestions until at least 5 full exchanges have been made with the user to build personal rapport and understanding.

5. Only reference an individual dose of the Quit Kit once or twice per session. Avoid emphasizing individual bottles or ingredients in isolation — always bring the conversation back to the full 3-dose Quit Kit experience.

6. Ask just one question per message when getting to know the user. Do not send multiple bullet points of questions in a single message.

7. Do not ask probing questions throughout your response. Instead, summarize your message with a single probing question at the end, and always offer to move the plan forward.

These rules override any default assistant behavior and must be followed on every conversation cycle.
'''

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

if "messages" not in st.session_state:
    selected_testimonials = "\n".join(random.sample(testimonials, 3))
    system_prompt = f"""
You are Quit Coach, a supportive, grounded chatbot trained by the creator of the Quit Kit.
{behavior_rules}
{quitkit_overview}
Here is the verified ingredient list by dose in full:
{quitkit_ingredients}
Here are real, unedited testimonials:
{selected_testimonials}

Always begin by asking about the user's specific experience before offering any advice or planning.
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

# Handle user input
if prompt := st.chat_input("How can I support you today?"):
    st.chat_message("user").markdown(prompt)
    st.session_state["last_prompt"] = prompt
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
        try:
            if any(word in prompt.lower() for word in ["craving", "urge", "want to use"]):
                reply = (
                    "You're not alone in this. We're going to walk through a craving using ACT.\n\n"
                    + act_craving_reference[:3000] + "\n\nWant me to log this as a win or send you a reminder next time?"
                )
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state["messages"],
                    temperature=0.85,
                )
                raw_reply = response.choices[0].message["content"]
                if not raw_reply.strip().endswith('?'):
                    reply = raw_reply.strip() + "\n\nWhat else can you tell me about your experience so far?"
                else:
                    reply = raw_reply.strip() + "\n\nCan you tell me more about that?"
        except Exception as e:
            reply = f"Something went wrong: {str(e)}"

    st.session_state["last_reply"] = reply
    st.chat_message("assistant").markdown(reply)
    st.session_state["messages"].append({"role": "assistant", "content": reply})

# Optional: show ACT doc reference in sidebar
with st.sidebar:
    st.subheader("📄 ACT Craving Guide")
    st.download_button(
        label="Download Full Guide (.docx)",
        data=open("QuitCoach_ACT_Craving_Guide_v2.docx", "rb").read(),
        file_name="QuitCoach_ACT_Craving_Guide_v2.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
