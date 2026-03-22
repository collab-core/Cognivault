import json
import re
from time import time
from typing import Dict, Tuple

from openai import OpenAI

from app.core.config import GROQ_API_KEY, GROQ_MODEL

_CACHE_TTL_SECONDS = 300
_RELEVANCE_CACHE: Dict[str, Tuple[float, bool, str]] = {}
_ACRONYM_EXPANSIONS = {
    "soa": "service oriented architecture",
}


def _cache_key(course_code: str, user_prompt: str) -> str:
    return f"{course_code.strip().lower()}::{user_prompt.strip().lower()}"


def _read_cache(key: str):
    cached = _RELEVANCE_CACHE.get(key)
    if not cached:
        return None
    ts, relevant, reason = cached
    if time() - ts > _CACHE_TTL_SECONDS:
        _RELEVANCE_CACHE.pop(key, None)
        return None
    return relevant, reason


def _write_cache(key: str, relevant: bool, reason: str):
    _RELEVANCE_CACHE[key] = (time(), relevant, reason)


def _heuristic_relevance(user_prompt: str, syllabus_context: str) -> Tuple[bool, str]:
    prompt = user_prompt.strip().lower()
    syllabus = (syllabus_context or "").strip().lower()

    if not prompt or not syllabus:
        return False, ""

    if prompt in syllabus:
        return True, "Prompt text appears directly in syllabus context"

    for acronym, expanded in _ACRONYM_EXPANSIONS.items():
        if acronym in prompt and expanded in syllabus:
            return True, f"Matched acronym '{acronym.upper()}' to syllabus topic '{expanded}'"
        if expanded in prompt and acronym in syllabus:
            return True, f"Matched topic '{expanded}' to acronym '{acronym.upper()}' in syllabus"

    prompt_tokens = {
        token
        for token in re.findall(r"[a-z0-9]+", prompt)
        if len(token) >= 4 and token not in {"what", "which", "where", "about", "different", "types"}
    }
    syllabus_tokens = {token for token in re.findall(r"[a-z0-9]+", syllabus) if len(token) >= 4}

    overlap = sorted(prompt_tokens.intersection(syllabus_tokens))
    if len(overlap) >= 2:
        return True, f"Matched syllabus keywords: {', '.join(overlap[:5])}"

    return False, ""


def classify_prompt_relevance(
    course_name: str,
    course_code: str,
    user_prompt: str,
    syllabus_context: str = "",
    conversation_context: str = "",
) -> Tuple[bool, str]:
    if not GROQ_API_KEY:
        return False, "LLM API key not configured - cannot verify relevance"

    key = _cache_key(course_code=course_code, user_prompt=user_prompt)
    cached = _read_cache(key)
    if cached:
        return cached

    heuristic_match, heuristic_reason = _heuristic_relevance(
        user_prompt=user_prompt,
        syllabus_context=syllabus_context,
    )
    if heuristic_match:
        _write_cache(key, True, heuristic_reason)
        return True, heuristic_reason

    try:
        client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

        system_prompt = (
            "You are a strict relevance classifier for course-scoped Q&A. "
            "Decide if the user's prompt is relevant to the given course syllabus. "
            "Use the syllabus context to decide. "
            "If conversation context is provided, use it to resolve pronouns (it, that, this, etc.). "
            "Return only compact JSON with keys: relevant (boolean), reason (string)."
        )

        user_message_parts = [
            f"Course: {course_name} ({course_code})",
            f"Syllabus context:\n{syllabus_context or 'No syllabus context provided'}",
        ]
        
        if conversation_context:
            user_message_parts.append(f"Recent conversation:\n{conversation_context}")
        
        user_message_parts.append(f"User prompt: {user_prompt}")
        user_message_parts.append("Is this prompt relevant to the course scope?")
        
        user_message = "\n\n".join(user_message_parts)

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0,
            max_tokens=150,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )

        content = response.choices[0].message.content or ""

        try:
            parsed = json.loads(content)
            result = (bool(parsed.get("relevant")), str(parsed.get("reason", "")))
            _write_cache(key, result[0], result[1])
            return result
        except json.JSONDecodeError:
            lowered = content.lower()
            is_relevant = "true" in lowered or "relevant" in lowered
            reason = content.strip() or "Classifier returned non-JSON response"
            _write_cache(key, is_relevant, reason)
            return is_relevant, reason
    
    except Exception as e:
        return False, f"Relevance check unavailable: {str(e)}"
