# recommendation_ui.py

import streamlit as st
import pandas as pd
from tutor_backend import recommend_topics, PREREQUISITES
from mastery_predictor import get_mastery_score

def show_recommendations(student_id, topics, feedback=None):
    use_predicted = False
    predicted_mastery = {}

    if feedback:
        predicted_score = get_mastery_score(feedback)
        predicted_mastery = {topics[0]: predicted_score}
        use_predicted = True

    recommended_topics = recommend_topics(
        student_id=student_id,
        topics=topics,
        use_predicted_mastery=use_predicted,
        predicted_mastery=predicted_mastery if use_predicted else None
    )

    if isinstance(recommended_topics, str) or not recommended_topics:
        st.warning("No recommendations available.")
        return

    st.markdown("### 🔍 Recommended Topics to Focus On")

    # Build a DataFrame with explanations
    table_data = []
    for item in recommended_topics:
        name = item.split(" (")[0]
        score = float(item.split("score: ")[-1].replace(")", ""))
        reason = "Prerequisites met, but low mastery score"
        if name in PREREQUISITES and PREREQUISITES[name]:
            unmet = [pr for pr in PREREQUISITES[name] if predicted_mastery.get(pr, 10) < 7]
            if unmet:
                reason = f"Locked — requires higher score in: {', '.join(unmet)}"
        table_data.append({"Topic": name, "Score": score, "Why": reason})

    df = pd.DataFrame(table_data)

    # Gradient-styled table
    st.dataframe(
        df.style.background_gradient(cmap="Reds", subset=["Score"]),
        use_container_width=True
    )

    # Add "Learn Now" buttons
    st.markdown("### ➕ Start Learning:")
    for t in df["Topic"]:
        if st.button(f"📖 Learn '{t}'", key=f"learn_{t}"):
            st.session_state.topic = t
            st.rerun()
