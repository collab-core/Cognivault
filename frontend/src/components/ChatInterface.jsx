import { useState, useRef, useEffect } from 'react'
import { chatWithContext } from '../api'

const STORAGE_KEY_PREFIX = 'syllabase_chat_'

function getStorageKey(courseId) {
  return `${STORAGE_KEY_PREFIX}${courseId}`
}

function loadChatFromStorage(courseId) {
  if (!courseId) return []
  try {
    const stored = localStorage.getItem(getStorageKey(courseId))
    return stored ? JSON.parse(stored) : []
  } catch (err) {
    console.error('Failed to load chat from storage:', err)
    return []
  }
}

function saveChatToStorage(courseId, messages) {
  if (!courseId) return
  try {
    localStorage.setItem(getStorageKey(courseId), JSON.stringify(messages))
  } catch (err) {
    console.error('Failed to save chat to storage:', err)
  }
}

function clearChatFromStorage(courseId) {
  if (!courseId) return
  try {
    localStorage.removeItem(getStorageKey(courseId))
  } catch (err) {
    console.error('Failed to clear chat from storage:', err)
  }
}

export default function ChatInterface({ activeContext }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [showClearConfirm, setShowClearConfirm] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  // Load chat from localStorage when course context changes
  useEffect(() => {
    if (activeContext?.course?.id) {
      const savedMessages = loadChatFromStorage(activeContext.course.id)
      setMessages(savedMessages)
    } else {
      setMessages([])
    }
    setInput('')
    setShowClearConfirm(false)
  }, [activeContext?.course?.id])

  async function handleSend() {
    const prompt = input.trim()
    if (!prompt || !activeContext || sending) return

    const userMsg = { id: Date.now(), role: 'user', content: prompt }
    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setInput('')
    setSending(true)

    // Build conversation history with sliding window (last 10 messages)
    const MAX_HISTORY_MESSAGES = 10
    const conversationHistory = newMessages
      .slice(-MAX_HISTORY_MESSAGES)
      .filter(msg => msg.role === 'user' || msg.role === 'assistant')
      .map(msg => ({
        role: msg.role,
        content: msg.role === 'user' ? msg.content : (msg.content || '')
      }))

    try {
      const result = await chatWithContext(
        activeContext.programme.id,
        activeContext.semester,
        activeContext.regulationYear,
        activeContext.course.id,
        prompt,
        conversationHistory,
      )

      const assistantMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        relevant: result.relevant,
        reason: result.reason,
        content: result.relevant ? result.answer : null,
      }
      const updatedMessages = [...newMessages, assistantMsg]
      setMessages(updatedMessages)
      saveChatToStorage(activeContext.course.id, updatedMessages)
    } catch (err) {
      const errorMsg = { id: Date.now() + 1, role: 'error', content: err.message }
      const updatedMessages = [...newMessages, errorMsg]
      setMessages(updatedMessages)
      saveChatToStorage(activeContext.course.id, updatedMessages)
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

  function handleClearChat() {
    clearChatFromStorage(activeContext.course.id)
    setMessages([])
    setShowClearConfirm(false)
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
            <button
              className="clear-chat-btn"
              onClick={() => setShowClearConfirm(true)}
              title="Clear chat history"
              aria-label="Clear chat history"
            >
              🗑️
            </button>
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

      {showClearConfirm && (
        <div className="modal-overlay" onClick={() => setShowClearConfirm(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Clear Chat History?</h3>
            <p>This will delete all messages in this course. This action cannot be undone.</p>
            <div className="modal-actions">
              <button className="modal-cancel" onClick={() => setShowClearConfirm(false)}>
                Cancel
              </button>
              <button className="modal-confirm" onClick={handleClearChat}>
                Clear Chat
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
