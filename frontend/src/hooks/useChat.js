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
      messages: [...prev.messages, userMsg],
      isStreaming: true,
      currentTool: null,
      error: null,
    }))

    const history = chatState.messages
      .filter(m => m.role === 'user' || m.role === 'assistant')
      .map(m => ({ role: m.role, content: m.content || '' }))

    let assistantContent = ''

    await streamChat(
      text.trim(),
      history,
      // onChunk — append text to last assistant message, or create one
      (chunk) => {
        assistantContent += chunk
        updateChat(prev => {
          const msgs = [...prev.messages]
          const last = msgs[msgs.length - 1]
          if (last && last.role === 'assistant' && !last.type) {
            msgs[msgs.length - 1] = { ...last, content: assistantContent }
          } else {
            msgs.push({ role: 'assistant', content: assistantContent, timestamp: Date.now() })
          }
          return { ...prev, messages: msgs, currentTool: null }
        })
      },
      // onDone
      () => updateChat(prev => ({ ...prev, isStreaming: false, currentTool: null })),
      // onError
      (err) => updateChat(prev => ({
        ...prev,
        isStreaming: false,
        currentTool: null,
        error: getErrorMsg(err),
      })),
      // onTool (legacy currentTool for ToolIndicator)
      (toolName) => updateChat(prev => ({ ...prev, currentTool: toolName })),
      tab,
      intent,
      null, // onAgent
      // onToolCall — add inline tool call card (pending)
      (toolCall) => {
        updateChat(prev => ({
          ...prev,
          currentTool: toolCall.name,
          messages: [
            ...prev.messages,
            {
              type: 'tool_call',
              id: `${toolCall.name}_${Date.now()}`,
              name: toolCall.name,
              args: toolCall.args,
              result: null,
            },
          ],
        }))
      },
      // onToolResult — patch the matching pending card with its result
      (toolResult) => {
        updateChat(prev => {
          const msgs = [...prev.messages]
          for (let i = msgs.length - 1; i >= 0; i--) {
            if (msgs[i].type === 'tool_call' && msgs[i].name === toolResult.name && msgs[i].result === null) {
              msgs[i] = { ...msgs[i], result: toolResult.result }
              break
            }
          }
          return { ...prev, messages: msgs, currentTool: null }
        })
      },
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
