from openai import OpenAI

from app.core.config import GROQ_API_KEY, GROQ_MODEL


def generate_answer(augmented_prompt: str) -> str:
    """Call Groq LLM with the syllabus-augmented prompt and return the answer."""
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured – cannot generate answer")

    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.3,
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful academic assistant for a university course. "
                    "Answer questions strictly based on the provided syllabus context. "
                    "Be clear, concise, and educational. "
                    "Use bullet points or numbered lists where appropriate."
                ),
            },
            {"role": "user", "content": augmented_prompt},
        ],
    )

    return response.choices[0].message.content or "No response was generated."
