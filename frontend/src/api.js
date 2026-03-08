const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function getSelections() {
  const res = await fetch(`${BASE_URL}/mcp/selections`)
  if (!res.ok) throw new Error(`Failed to load selections: ${res.statusText}`)
  return res.json()
}

export async function getCourses(programmeId, semester, regulationYear) {
  const params = new URLSearchParams({
    programme_id: programmeId,
    semester: String(semester),
    regulation_year: String(regulationYear),
  })
  const res = await fetch(`${BASE_URL}/mcp/courses?${params}`)
  if (!res.ok) throw new Error(`Failed to load courses: ${res.statusText}`)
  return res.json()
}

export async function chatWithContext(programmeId, semester, regulationYear, courseId, userPrompt) {
  const res = await fetch(`${BASE_URL}/mcp/chat`, {
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
    }),
  })
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}))
    throw new Error(detail.detail || `Request failed: ${res.statusText}`)
  }
  return res.json()
}
