import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './index.css'

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
      <App />
    </QueryClientProvider>
  </React.StrictMode>
)

/* ── Register Service Worker for PWA / Installability ── */
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(err => {
      console.log('SW registration failed: ', err);
    });
  });
}
