const BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

async function requestJson(path, options) {
  try {
    const res = await fetch(`${BASE_URL}${path}`, options)
    if (!res.ok) {
      const detail = await res.json().catch(() => ({}))
      throw new Error(detail.detail || `Request failed: ${res.status} ${res.statusText}`)
    }
    return res.json()
  } catch (err) {
    if (err instanceof TypeError) {
      throw new Error(`Cannot reach backend at ${BASE_URL}. Check VITE_API_URL and backend CORS settings.`)
    }
    throw err
  }
}

export async function getSelections() {
  return requestJson('/mcp/selections')
}

export async function getCourses(programmeId, semester, regulationYear) {
  const params = new URLSearchParams({
    programme_id: programmeId,
    semester: String(semester),
    regulation_year: String(regulationYear),
  })
  return requestJson(`/mcp/courses?${params}`)
}

export async function chatWithContext(programmeId, semester, regulationYear, courseId, userPrompt, conversationHistory = []) {
  return requestJson('/mcp/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      selection: {
        programme_id: programmeId,
        semester,
        regulation_year: regulationYear,
      },
      course_id: courseId,
      user_prompt: userPrompt,
      conversation_history: conversationHistory,
    }),
  })
}
