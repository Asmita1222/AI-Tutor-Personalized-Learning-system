import streamlit as st
import pandas as pd
from tutor_backend import (
    update_student_progress,
    load_student_progress,
    get_student_learning_path,
    recommend_topics,
    PREREQUISITES,
)
from convex_optimizer import optimize_learning_path
from quiz_generator import get_explanation, generate_quiz, answer_student_question
from mastery_predictor import get_mastery_score
from recommendation_ui import show_recommendations  # custom module you create

def main():
    st.set_page_config(page_title="AI Tutor", layout="wide")
    st.title("🤖 AI Tutor - Personalized Learning")

    # --- SIDEBAR: Ask Any Question ---
    with st.sidebar:
        st.header("💬 Ask the AI Tutor")
        user_question = st.text_area("Type your question here:")

        if st.button("🧠 Ask", key="ask_button"):
            if user_question.strip():
                with st.spinner("Thinking..."):
                    response = answer_student_question(user_question, level="beginner")
                st.markdown("### 🤖 Tutor's Answer:")
                st.write(response)
            else:
                st.warning("Please enter a question.")

    # --- Student Info Input ---
    student_id = st.text_input("Enter Student ID:", key="student_id")

    # Dictionary of subjects with their respective topics
    subjects_and_topics = {
        "Data Science": [
            "MySQL",
            "Data Structures and Algorithms",
            "Power BI",
            "Pandas",
            "NumPy",
            "Machine Learning",
            "Statistics",
            "Python Basics",
            "EDA (Exploratory Data Analysis)",
            "Matplotlib & Seaborn",
        ],
        "Computer Science": ["Algorithms", "Operating Systems", "Networking"],
        "Mathematics": ["Calculus", "Linear Algebra", "Probability"]
    }

    # Subject selection from the dictionary
    selected_subject = st.selectbox("📘 Choose a Subject:", list(subjects_and_topics.keys()), key="subject")

    # Topic selection based on the selected subject
    selected_topic = st.selectbox(
        "📚 Choose a Topic:",
        subjects_and_topics[selected_subject],  # Get topics based on the selected subject
        key="topic"
    )

    # Display the selected subject and topic
    st.write(f"### Subject: {selected_subject}")
    st.write(f"### Topic: {selected_topic}")

    # Learning Level Input
    level = st.selectbox("Learning Level:", ["beginner", "intermediate", "advanced"], key="level")

    # --- Generate Quiz ---
    if st.button("📝 Take Quiz", key="quiz_button"):
        quiz_data = generate_quiz(selected_topic, "medium")

        if not quiz_data:
            st.warning("Quiz couldn't be generated. Try again.")
        else:
            st.session_state.quiz_answers = {}
            st.session_state.quiz_data = quiz_data

    # --- Quiz Display & Submission ---
    if "quiz_data" in st.session_state:
        st.markdown("### 🧪 Answer the Quiz")

        for i, q in enumerate(st.session_state.quiz_data):
            question_key = f"q_{i}"
            st.session_state.quiz_answers[question_key] = st.radio(
                f"Q{i+1}: {q['question']}",
                q["options"],
                key=question_key
            )

        if st.button("✅ Submit Quiz", key="submit_quiz"):
            score = 0
            wrong_feedback = []

            for i, q in enumerate(st.session_state.quiz_data):
                user_answer = st.session_state.quiz_answers[f"q_{i}"]
                correct = q["correct"]
                if user_answer == correct:
                    score += 1
                else:
                    wrong_feedback.append({
                        "question": q["question"],
                        "your_answer": user_answer,
                        "correct": correct,
                        "explanation": q.get("explanations", {}).get(user_answer, "No explanation provided.")
                    })

            mastery_score = round((score / len(st.session_state.quiz_data)) * 10, 2)
            st.success(f"You scored {score} out of {len(st.session_state.quiz_data)}")
            st.info(f"Mastery Score Recorded: {mastery_score}/10")
            update_student_progress(student_id, selected_topic, mastery_score)
            st.success("📚 Progress saved successfully!")

            if wrong_feedback:
                st.markdown("### ❌ Review Mistakes")
                for fb in wrong_feedback:
                    st.error(f"**Q: {fb['question']}**")
                    st.write(f"Your Answer: ❌ {fb['your_answer']}")
                    st.write(f"Correct Answer: ✅ {fb['correct']}")
                    st.info(f"💡 {fb['explanation']}")

        if st.button("🔁 Retry Quiz", key="retry_quiz"):
            st.session_state.pop("quiz_data", None)
            st.session_state.pop("quiz_answers", None)

    # --- Predict & Optimize Learning Path ---
    with st.expander("🚀 Personalized Learning Plan for This Topic", expanded=True):
        st.subheader(f"📘 Topic: {selected_topic}")

        feedback = st.text_area(
            f"✏️ How well do you understand '{selected_topic}'?",
            key=f"feedback_{selected_topic}",
            placeholder="e.g., I struggle with this topic or find it easy to understand.",
            height=100
        ) or f"The student has average skills in {selected_topic}."

        col1, col2 = st.columns(2)
        if col1.button("🧠 Predict & Optimize", key="optimize_button"):
            predicted_score = get_mastery_score(feedback)
            predicted_mastery = {selected_topic: predicted_score}
            difficulty_levels = [6]  # Placeholder
            optimized_hours = optimize_learning_path(student_id, [selected_topic], difficulty_levels)

            st.success("✅ Prediction Completed!")
            st.markdown("**📊 Predicted Mastery Level (0-10):**")
            st.write(predicted_mastery)
            st.markdown("**⏳ Recommended Study Time (hours):**")
            st.write(optimized_hours)

        if col2.button("🎯 Recommend Topics", key="recommend_button"):
            feedback_key = f"feedback_{selected_topic}"
            feedback = st.session_state.get(feedback_key, "")
            show_recommendations(student_id, subjects_and_topics[selected_subject], feedback=feedback)


if __name__ == "__main__":
    main()
