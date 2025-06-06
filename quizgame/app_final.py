import streamlit as st
import random
from quiz_data import quiz_questions

# Set up session state to store score, index, and selections
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

st.title("🧠 Ultimate Quiz Game")

# Category selection
if not st.session_state.category:
    st.subheader("Choose a Category:")
    category = st.selectbox("Select quiz category", list(quiz_questions.keys()))
    if st.button("Start Quiz"):
        st.session_state.category = category
        st.session_state.shuffled_questions = random.sample(quiz_questions[category], len(quiz_questions[category]))
        st.rerun()
else:
    category = st.session_state.category
    questions = st.session_state.shuffled_questions
    q_index = st.session_state.question_index

    if q_index < len(questions):
        question = questions[q_index]
        st.write(f"**Q{q_index + 1}: {question['question']}**")
        user_answer = st.radio("Choose an answer:", question["options"], key=q_index)

        if st.button("Submit"):
            st.session_state.user_answers.append({
                "question": question["question"],
                "selected": user_answer,
                "correct": question["answer"]
            })

            if user_answer == question["answer"]:
                st.session_state.score += 1

            st.session_state.question_index += 1
            st.rerun()
    else:
        st.success("Quiz Complete! 🎉")
        st.write(f"**Your Score: {st.session_state.score} / {len(questions)}**")

        with st.expander("Review your answers"):
            for ans in st.session_state.user_answers:
                st.write(f"**Q:** {ans['question']}")
                st.write(f"Your answer: {ans['selected']}")
                st.write(f"Correct answer: {ans['correct']}")
                st.markdown("---")

        if st.button("Play Again"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
