
import streamlit as st
import random
import time
import os
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from quiz_data import quiz_questions

LEADERBOARD_FILE = "leaderboard.csv"

# Initialize session state variables
if "category" not in st.session_state:
    st.session_state.category = None
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "shuffled_questions" not in st.session_state:
    st.session_state.shuffled_questions = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = []
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "username" not in st.session_state:
    st.session_state.username = ""

st.title("🧠 Ultimate Quiz Game")

# Load leaderboard
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        df = pd.read_csv(LEADERBOARD_FILE)
        return df.sort_values(by="score", ascending=False)
    else:
        return pd.DataFrame(columns=["username", "score"])

# Save score to leaderboard
def save_score(name, score):
    df = load_leaderboard()
    new_entry = pd.DataFrame({"username": [name], "score": [score]})
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(LEADERBOARD_FILE, index=False)

leaderboard_df = load_leaderboard()

# Show leaderboard on start
if not st.session_state.category:
    st.subheader("🏆 Leaderboard - Top 5 Scores")
    if leaderboard_df.empty:
        st.write("No scores yet. Be the first to conquer the quiz!")
    else:
        st.table(leaderboard_df.head(5))

    st.subheader("Enter your name to start:")
    st.session_state.username = st.text_input("Your name")

    st.subheader("Choose a Category:")
    category = st.selectbox("Select quiz category", list(quiz_questions.keys()))

    if st.button("Start Quiz"):
        if st.session_state.username.strip() == "":
            st.warning("Please enter your name to proceed.")
        else:
            st.session_state.category = category
            st.session_state.shuffled_questions = random.sample(
                quiz_questions[category], len(quiz_questions[category])
            )
            st.session_state.start_time = time.time()
            st.session_state.question_index = 0
            st.session_state.score = 0
            st.session_state.user_answers = []
            st.experimental_memo.clear()
            st.experimental_rerun()

else:
    category = st.session_state.category
    questions = st.session_state.shuffled_questions
    q_index = st.session_state.question_index

    # Auto-refresh every 1 second, up to 15 counts (15 seconds timer)
    count = st_autorefresh(interval=1000, limit=15, key="timer")
    remaining_time = 15 - count

    if q_index < len(questions):
        question = questions[q_index]

        st.write(f"**Q{q_index + 1}: {question['question']}**")

        if remaining_time > 0:
            st.info(f"⏳ Time left: {remaining_time} seconds")

            user_answer = st.radio("Choose an answer:", question["options"], key=q_index)

            if st.button("Submit", key=f"submit_{q_index}"):
                st.session_state.user_answers.append({
                    "question": question["question"],
                    "selected": user_answer,
                    "correct": question["answer"]
                })
                if user_answer == question["answer"]:
                    st.session_state.score += 1
                st.session_state.question_index += 1
                st.session_state.start_time = time.time()
                st.experimental_memo.clear()
                st.experimental_rerun()
        else:
            st.warning("⏰ Time's up! Moving to next question...")

            if st.button("Continue", key=f"continue_{q_index}"):
                st.session_state.user_answers.append({
                    "question": question["question"],
                    "selected": "No Answer (Timed Out)",
                    "correct": question["answer"]
                })
                st.session_state.question_index += 1
                st.session_state.start_time = time.time()
                st.experimental_memo.clear()
                st.experimental_rerun()

    else:
        st.success("Quiz Complete! 🎉")
        st.write(f"**Your Score: {st.session_state.score} / {len(questions)}**")

        # Save score to leaderboard
        save_score(st.session_state.username, st.session_state.score)

        with st.expander("Review your answers"):
            for ans in st.session_state.user_answers:
                st.write(f"**Q:** {ans['question']}")
                st.write(f"Your answer: {ans['selected']}")
                st.write(f"Correct answer: {ans['correct']}")
                st.markdown("---")

        if st.button("Play Again"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_memo.clear()
            st.experimental_rerun()
