const BASE = 'http://localhost:8000'

export async function streamChat(message, history, onChunk, onDone, onError, onTool) {
  let response
  try {
    response = await fetch(`${BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        conversation_history: history,
        user_id: getUserId(),
      }),
    })
  } catch {
    onError('backend_offline')
    return
  }

  if (response.status === 401) {
    onError('auth_expired')
    return
  }
  if (!response.ok) {
    onError('server_error')
    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop()

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      try {
        const data = JSON.parse(line.slice(6))
        if (data.done) {
          onDone()
          return
        }
        if (data.error) {
          onError(data.error)
          return
        }
        if (data.tool) {
          onTool?.(data.tool)
          continue
        }
        if (data.text) {
          onChunk(data.text)
        }
      } catch {
        // malformed SSE line, skip
      }
    }
  }

  onDone()
}

export async function getAuthStatus() {
  try {
    const res = await fetch(`${BASE}/auth/status?user_id=${getUserId()}`)
    if (!res.ok) return { authenticated: false }
    return res.json()
  } catch {
    return { authenticated: false, offline: true }
  }
}

export function loginWithSwiggy() {
  window.location.href = `${BASE}/auth/login?user_id=${getUserId()}`
}

export function getUserId() {
  let id = localStorage.getItem('swiggyos_user_id')
  if (!id) {
    id = `user_${Math.random().toString(36).slice(2, 10)}`
    localStorage.setItem('swiggyos_user_id', id)
  }
  return id
}
