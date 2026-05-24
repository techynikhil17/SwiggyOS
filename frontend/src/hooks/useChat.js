import { useCallback } from 'react'
import { streamChat } from '../api/chat'

function getErrorMsg(err) {
  if (err === 'backend_offline')
    return 'Backend offline. Start the server with: cd backend && uvicorn main:app --reload'
  if (err === 'auth_expired')
    return 'Your Swiggy session expired. Please reconnect.'
  return 'Something went wrong. Please try again.'
}

export function useChat({ tab, chatState, updateChat }) {
  const sendMessage = useCallback(async (text, intent = null) => {
    if (chatState.isStreaming || !text.trim()) return

    const userMsg = { role: 'user', content: text.trim(), timestamp: Date.now() }

    updateChat(prev => ({
      ...prev,
      messages: [
        ...prev.messages,
        userMsg,
        { role: 'assistant', content: '', timestamp: Date.now() },
      ],
      isStreaming: true,
      currentTool: null,
      error: null,
    }))

    const history = chatState.messages.map(m => ({ role: m.role, content: m.content }))
    let assistantContent = ''

    await streamChat(
      text.trim(),
      history,
      (chunk) => {
        assistantContent += chunk
        updateChat(prev => {
          const msgs = [...prev.messages]
          msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], content: assistantContent }
          return { ...prev, messages: msgs, currentTool: null }
        })
      },
      () => updateChat(prev => ({ ...prev, isStreaming: false, currentTool: null })),
      (err) => updateChat(prev => ({
        ...prev,
        isStreaming: false,
        currentTool: null,
        messages: prev.messages.slice(0, -1),
        error: getErrorMsg(err),
      })),
      (toolName) => updateChat(prev => ({ ...prev, currentTool: toolName })),
      tab,
      intent,
    )
  }, [tab, chatState.isStreaming, chatState.messages, updateChat])

  const clearHistory = useCallback(() => {
    updateChat(() => ({
      messages: [],
      isStreaming: false,
      currentTool: null,
      error: null,
      budget: { total: 0, spent: 0 },
    }))
  }, [updateChat])

  return { sendMessage, clearHistory }
}
