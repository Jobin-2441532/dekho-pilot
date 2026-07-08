import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import posthog from 'posthog-js'
import { PostHogProvider } from 'posthog-js/react'
import App from './App'
import './index.css'

/* ── PostHog Initialization ── */
// Using Vite env vars instead of NEXT_PUBLIC since this is a Vite app
if (typeof window !== 'undefined') {
  posthog.init(import.meta.env.VITE_POSTHOG_KEY || 'phc_placeholder_key', {
    api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://app.posthog.com',
    loaded: (posthog) => {
      if (import.meta.env.DEV) posthog.debug(false) // Disable debug in dev to reduce noise
    },
    // Don't auto-capture anything beyond page views per spec
    autocapture: false,
    session_recording: {
      maskAllInputs: false
    }
  })
}

/* ── TanStack Query client — configured for fintech data ── */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime:        1000 * 60 * 5,   // 5 min — financial data doesn't change every second
      gcTime:           1000 * 60 * 30,  // 30 min cache
      retry:            1,
      refetchOnWindowFocus: false,       // avoid jarring refetches mid-session
    },
  },
})

/* ── Apply persisted theme before first render (avoids flash) ── */
const savedStore = localStorage.getItem('dekho-app-store')
if (savedStore) {
  try {
    const { state } = JSON.parse(savedStore)
    if (state?.theme) {
      document.documentElement.setAttribute('data-theme', state.theme)
    }
  } catch {
    document.documentElement.setAttribute('data-theme', 'light')
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <PostHogProvider client={posthog}>
        <App />
      </PostHogProvider>
    </QueryClientProvider>
  </React.StrictMode>
)

