import tensorflow_hub as hub
import numpy as np

# Load Universal Sentence Encoder once
model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

def get_mastery_score(statement):
    embedding = model([statement]).numpy()[0]
    score = np.linalg.norm(embedding)
    return round(min(score, 10.0), 2)  # Ensure it's in 0–10 range

def get_mastery_for_topics(topics, feedbacks):
    return {topic: get_mastery_score(fb) for topic, fb in zip(topics, feedbacks)}
