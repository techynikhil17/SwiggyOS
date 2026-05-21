import { useState, useCallback } from 'react'
import { streamChat } from '../api/chat'

const TOOL_PATTERN = /^\[TOOL:([^\]]+)\]/

export function useChat() {
  const [messages, setMessages] = useState([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentTool, setCurrentTool] = useState(null)
  const [budget, setBudget] = useState({ total: 0, spent: 0 })
  const [error, setError] = useState(null)

  const sendMessage = useCallback(async (text) => {
    if (isStreaming || !text.trim()) return

    const userMsg = {
      role: 'user',
      content: text.trim(),
      timestamp: Date.now(),
    }

    setMessages(prev => [...prev, userMsg])
    setIsStreaming(true)
    setCurrentTool(null)
    setError(null)

    const history = messages.map(m => ({ role: m.role, content: m.content }))

    let assistantContent = ''
    const assistantMsg = {
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
    }

    setMessages(prev => [...prev, { ...assistantMsg }])

    await streamChat(
      text.trim(),
      history,
      (chunk) => {
        const toolMatch = chunk.match(TOOL_PATTERN)
        if (toolMatch) {
          setCurrentTool(toolMatch[1])
          chunk = chunk.replace(TOOL_PATTERN, '').trim()
        } else if (assistantContent.length > 0) {
          setCurrentTool(null)
        }

        if (chunk) {
          assistantContent += chunk
          setMessages(prev => {
            const updated = [...prev]
            updated[updated.length - 1] = {
              ...updated[updated.length - 1],
              content: assistantContent,
            }
            return updated
          })
        }
      },
      () => {
        setIsStreaming(false)
        setCurrentTool(null)
      },
      (err) => {
        setIsStreaming(false)
        setCurrentTool(null)
        if (err === 'backend_offline') {
          setError('Backend offline. Start the server with: cd backend && uvicorn main:app --reload')
        } else if (err === 'auth_expired') {
          setError('Your Swiggy session expired. Please reconnect.')
        } else {
          setError('Something went wrong. Please try again.')
        }
        setMessages(prev => prev.slice(0, -1))
      },
    )
  }, [isStreaming, messages])

  const clearHistory = useCallback(() => {
    setMessages([])
    setCurrentTool(null)
    setError(null)
  }, [])

  return { messages, isStreaming, currentTool, budget, setBudget, error, setError, sendMessage, clearHistory }
}
