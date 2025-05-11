import json
import os

STUDENT_DATA_FILE = "student_data.json"


PREREQUISITES = {
    # 🧪 Data Science
    "Python Basics": [],
    "NumPy": ["Python Basics"],
    "Pandas": ["Python Basics", "NumPy"],
    "MySQL": [],
    "Statistics": ["Python Basics"],
    "Data Structures and Algorithms": ["Python Basics"],
    "EDA (Exploratory Data Analysis)": ["Pandas", "Statistics"],
    "Matplotlib & Seaborn": ["Pandas"],
    "Power BI": ["Statistics"],
    "Machine Learning": ["Statistics", "Linear Algebra", "Data Structures and Algorithms"],

    # 💻 Computer Science
    "Algorithms": ["Data Structures and Algorithms"],
    "Operating Systems": [],
    "Networking": ["Operating Systems"],

    # 📐 Mathematics
    "Calculus": [],
    "Linear Algebra": [],
    "Probability": ["Statistics"]
}


def load_student_progress():
    """Load student progress from JSON file, handling empty or missing files safely."""
    if not os.path.exists(STUDENT_DATA_FILE) or os.stat(STUDENT_DATA_FILE).st_size == 0:
        return {}  # Return an empty dictionary if file is empty/missing

    try:
        with open(STUDENT_DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}  # Return an empty dictionary if JSON is invalid

def save_student_progress(student_data):
    """Save student progress to JSON file."""
    with open(STUDENT_DATA_FILE, "w") as f:
        json.dump(student_data, f, indent=4)

def update_student_progress(student_id, topic, score):
    student_data = load_student_progress()

    if student_id not in student_data:
        student_data[student_id] = {}

    student_data[student_id][topic] = score  # Store score per topic

    save_student_progress(student_data)  # Save updated progress

def get_student_learning_path(student_id, selected_subject):
    student_data = load_student_progress()

    # Fallback: if student or subject not found, return a message
    if student_id not in student_data:
        return [f"No data found for student ID {student_id}."]

    student_scores = student_data[student_id]

    # Filter scores for the selected subject
    relevant_topics = {
        topic: score
        for topic, score in student_scores.items()
        if selected_subject.lower() in topic.lower()
    }

    if not relevant_topics:
        return [f"No progress data for subject '{selected_subject}'"]

    # Sort topics by score (ascending) to prioritize weaker topics
    sorted_topics = sorted(relevant_topics.items(), key=lambda item: item[1])

    # Recommend top 3 weak topics
    recommended = [f"{topic} (score: {score})" for topic, score in sorted_topics[:3]]

    return recommended

def recommend_topics(student_id, topics, use_predicted_mastery=False, predicted_mastery=None):
    """
    Recommend topics based on lowest mastery and prerequisite logic.

    Args:
        student_id (str): ID of the student
        topics (list): List of topic names to consider
        use_predicted_mastery (bool): Whether to use predicted scores
        predicted_mastery (dict): If using predicted scores, provide them here

    Returns:
        list: Recommended topics (up to 3)
    """
    if use_predicted_mastery and predicted_mastery:
        mastery = predicted_mastery
    else:
        student_data = load_student_progress()
        if student_id not in student_data:
            return ["No progress data found for this student."]

        mastery = student_data[student_id]

    # Fill missing scores with default
    mastery_scores = {t: mastery.get(t, 0) for t in topics}

    # Apply prerequisite logic: only allow topics if prerequisites are mastered (>7)
    def prerequisites_met(topic):
        return all(mastery_scores.get(pr, 0) >= 7 for pr in PREREQUISITES.get(topic, []))

    eligible_topics = [t for t in topics if prerequisites_met(t)]

    # Sort by mastery (ascending)
    sorted_topics = sorted(eligible_topics, key=lambda t: mastery_scores[t])

    return [f"{t} (score: {mastery_scores[t]})" for t in sorted_topics[:3]]

