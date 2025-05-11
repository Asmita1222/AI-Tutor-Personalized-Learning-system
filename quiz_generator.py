import google.generativeai as genai
import json

# Configure Gemini AI
genai.configure(api_key="Your API KEY HERE")


def get_explanation(topic, level):
    model = genai.GenerativeModel("gemini-1.5-pro")
    prompt = f"Explain the topic '{topic}' in simple terms for a {level}-level student."
    response = model.generate_content(prompt)
    return response.text if hasattr(response, "text") else str(response)

def answer_student_question(question, level="beginner"):
    model = genai.GenerativeModel("gemini-1.5-pro")
    prompt = f"Answer this question as if you're tutoring a {level}-level student:\n\n{question}"
    response = model.generate_content(prompt)
    return response.text if hasattr(response, "text") else str(response)


def generate_quiz(topic, difficulty):
    model = genai.GenerativeModel("gemini-1.5-pro")
    prompt = (
        f"Create a {difficulty}-level quiz with 5 multiple-choice questions on the topic: {topic}. "
        f"Each question must include:\n"
        f"- 'question': string\n"
        f"- 'options': list of 4 strings\n"
        f"- 'correct': the correct option string\n"
        f"- 'explanation': a short explanation of each question why the correct answer is right\n"
        f"Return the quiz as a **JSON array** of objects (no markdown, no formatting)."
    )
    response = model.generate_content(prompt)
    
    try:
        # Clean and parse Gemini's response
        text = response.text.strip()

        # If it starts with a markdown block, strip it
        if text.startswith("```json"):
            text = text.split("```json")[1].split("```")[0].strip()
        
        quiz_json = json.loads(text)
        return quiz_json
    except Exception as e:
        print("❌ Failed to parse quiz:", e)
        return []
