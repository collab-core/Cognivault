import { useState, useRef, useEffect } from 'react'
import { chatWithContext } from '../api'

export default function ChatInterface({ activeContext }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  // Reset chat when course context changes
  useEffect(() => {
    setMessages([])
    setInput('')
  }, [activeContext?.course?.id])

  async function handleSend() {
    const prompt = input.trim()
    if (!prompt || !activeContext || sending) return

    const userMsg = { id: Date.now(), role: 'user', content: prompt }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setSending(true)

    try {
      const result = await chatWithContext(
        activeContext.programme.id,
        activeContext.semester,
        activeContext.regulationYear,
        activeContext.course.id,
        prompt,
      )

      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          relevant: result.relevant,
          reason: result.reason,
          content: result.relevant ? result.answer : null,
        },
      ])
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { id: Date.now() + 1, role: 'error', content: err.message },
      ])
    } finally {
      setSending(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const hasContext = !!activeContext

  return (
    <main className="chat-panel">
      <div className="chat-header">
        {hasContext ? (
          <>
            <div className="course-badge">{activeContext.course.code}</div>
            <div className="course-title">{activeContext.course.name}</div>
            <div className="course-meta">
              Sem {activeContext.semester} &middot; Reg {activeContext.regulationYear}
            </div>
          </>
        ) : (
          <div className="no-context-hint">
            ← Select a programme, semester, regulation year, and course to start
          </div>
        )}
      </div>

      <div className="messages-area">
        {messages.length === 0 && hasContext && (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <p>Ask anything about <strong>{activeContext.course.name}</strong></p>
            <p className="empty-hint">I'll answer based strictly on the course syllabus.</p>
          </div>
        )}

        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.role}`}>
            {msg.role === 'user' && (
              <div className="bubble user-bubble">{msg.content}</div>
            )}

            {msg.role === 'assistant' && msg.relevant && (
              <div className="bubble assistant-bubble">{msg.content}</div>
            )}

            {msg.role === 'assistant' && !msg.relevant && (
              <div className="bubble irrelevant-bubble">
                <span className="irrelevant-icon">⚠️</span>
                <div>
                  <p className="irrelevant-title">Not within syllabus scope</p>
                  <p className="irrelevant-reason">{msg.reason}</p>
                </div>
              </div>
            )}

            {msg.role === 'error' && (
              <div className="bubble error-bubble">⚠️ {msg.content}</div>
            )}
          </div>
        ))}

        {sending && (
          <div className="message assistant">
            <div className="bubble assistant-bubble typing">
              <span /><span /><span />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <textarea
          placeholder={
            hasContext
              ? `Ask about ${activeContext.course.code}… (Enter to send, Shift+Enter for new line)`
              : 'Select a course from the sidebar to begin…'
          }
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={!hasContext || sending}
          rows={3}
        />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={!hasContext || !input.trim() || sending}
          aria-label="Send"
        >
          {sending ? (
            <span className="send-spinner" />
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          )}
        </button>
      </div>
    </main>
  )
}
