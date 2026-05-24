import { useState, useCallback } from 'react'

const TABS = ['food', 'instamart', 'dineout', 'all']

const EMPTY_CHAT = () => ({
  messages: [],
  isStreaming: false,
  currentTool: null,
  error: null,
  budget: { total: 0, spent: 0 },
})

export function useTabChats() {
  const [chats, setChats] = useState(
    Object.fromEntries(TABS.map(t => [t, EMPTY_CHAT()]))
  )
  const [activeTab, setActiveTab] = useState('food')

  const updateChat = useCallback((tab, updater) => {
    setChats(prev => ({ ...prev, [tab]: updater(prev[tab]) }))
  }, [])

  const getTabContext = useCallback((tab, n = 10) => {
    return chats[tab].messages.slice(-n)
  }, [chats])

  return { chats, activeTab, setActiveTab, updateChat, getTabContext }
}
