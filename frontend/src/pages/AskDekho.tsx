/* AskDekho — chatbot accessed via floating FAB
   This route is kept for direct deep-linking / back-compat.
   The primary entrypoint is the ChatbotFAB visible on all screens. */
import { useEffect } from 'react'
import { useAppStore } from '../store/appStore'

export default function AskDekho() {
  const { openChat } = useAppStore()

  // Auto-open the chat panel when this route is visited directly
  useEffect(() => {
    openChat()
  }, [openChat])

  return null  // Chat panel renders inside AppShell via ChatbotFAB
}
