import cvxpy as cp
import numpy as np
from tutor_backend import load_student_progress

def optimize_learning_path(student_id, topics, difficulty_levels):
    """
    Optimizes the number of study hours to assign to each topic based on mastery and difficulty.

    Args:
        student_id (str): ID of the student.
        topics (list of str): List of topic names.
        difficulty_levels (list of float): List of difficulty values for each topic.

    Returns:
        dict: Dictionary with topic names as keys and recommended study hours as values.
    """
    student_data = load_student_progress()
    student_scores = student_data.get(student_id, {})

    # Convert scores (0-10) to mastery levels (0 = weak, 1 = strong)
    mastery_levels = np.array([student_scores.get(topic, 0) / 10 for topic in topics])
    difficulty_levels = np.array(difficulty_levels)

    num_topics = len(topics)
    x = cp.Variable(num_topics)  # study hours per topic

    # Objective: penalize more time spent on already strong areas
    objective = cp.Minimize(cp.sum_squares(cp.multiply((1 - mastery_levels) * difficulty_levels, x)))

    # Constraints
    constraints = [
        cp.sum(x) >= 4,      # Minimum total study time
        x >= 0,              # No negative time
        x <= 5               # Max 5 hours per topic
    ]

    problem = cp.Problem(objective, constraints)

    try:
        problem.solve()
        if x.value is None:
            print("⚠️ Optimization failed. No solution.")
            return {topic: 0 for topic in topics}

        recommended_hours = {topic: round(hour, 2) for topic, hour in zip(topics, x.value)}
        print(f"🚀 Optimized Study Hours: {recommended_hours}")
        return recommended_hours

    except Exception as e:
        print(f"❌ Optimization error: {e}")
        return {topic: 0 for topic in topics}
