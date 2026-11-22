import os
import streamlit as st
import requests


def show_ai_assistant():

    st.title("🤖 AI Career Assistant")

    api_key = os.getenv("GROQ_API_KEY")

    model = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    )

    task = st.selectbox(
        "Choose a task",
        [
            "Resume Review",
            "Job Description Analysis",
            "Skill Gap Analysis",
            "Interview Preparation",
            "Company Interview Preparation",
            "Project Ideas",
            "Career Roadmap",
            "HR Interview Practice",
            "Technical Interview Practice"
        ]
    )

    context = st.text_area(
        "Paste resume, job description, or other context",
        height=200
    )

    question = st.text_area(
        "Your question"
    )

    if st.button("Generate AI Guidance"):

        if not context.strip() and not question.strip():
            st.warning("Enter some information first.")
            return

        if not api_key:
            st.error("Groq API key is missing.")
            return

        prompt = f"""
You are an expert career mentor for a Computer Science student.

Task: {task}

Context:
{context}

Question:
{question}

Give specific, practical, clear advice with actionable steps.
"""

        try:

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.4,
                    "max_tokens": 2000
                },
                timeout=60
            )

            response.raise_for_status()

            answer = response.json()["choices"][0]["message"]["content"]

            st.subheader("AI Response")
            st.markdown(answer)

        except Exception as error:
            st.error(f"Error: {error}")