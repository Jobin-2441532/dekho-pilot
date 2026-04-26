import { useEffect } from 'react'
import { useAppStore } from '../store/appStore'

export type Theme = 'light' | 'dark'

export function useTheme() {
  const { theme, setTheme } = useAppStore()

  // Apply theme to <html> element whenever it changes
  useEffect(() => {
    const root = document.documentElement
    root.setAttribute('data-theme', theme)

    // Update PWA theme-color meta tag
    const meta = document.querySelector('meta[name="theme-color"]')
    if (meta) {
      meta.setAttribute(
        'content',
        theme === 'light' ? '#5C3D2E' : '#0F131C'
      )
    }
  }, [theme])

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  const isDark = theme === 'dark'
  const isLight = theme === 'light'

  return { theme, toggleTheme, setTheme, isDark, isLight }
}
