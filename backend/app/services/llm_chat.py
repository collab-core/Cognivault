from openai import OpenAI

from app.core.config import GROQ_API_KEY, GROQ_MODEL


def generate_answer(augmented_prompt: str, conversation_history: list = None) -> str:
    """Call Groq LLM with the syllabus-augmented prompt and return the answer."""
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured – cannot generate answer")

    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful academic assistant for a university course. "
                "Answer questions strictly based on the provided syllabus context. "
                "Be clear, concise, and educational. "
                "Use bullet points or numbered lists where appropriate."
            ),
        }
    ]

    # Add conversation history if provided (last N messages for context)
    if conversation_history:
        # Limit history to avoid token overflow (keep last 12 messages max)
        recent_history = conversation_history[-12:]
        messages.extend(recent_history)

    # Add the current question with syllabus context
    messages.append({"role": "user", "content": augmented_prompt})

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.3,
        max_tokens=1024,
        messages=messages,
    )

    return response.choices[0].message.content or "No response was generated."
