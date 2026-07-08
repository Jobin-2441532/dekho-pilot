import { useRef, useCallback } from 'react'

/**
 * Returns a debounced version of the given callback.
 * @param fn - Function to debounce
 * @param delay - Debounce delay in ms (default: 200)
 */
export function useDebounce<T extends (...args: Parameters<T>) => void>(
  fn: T,
  delay = 200,
): (...args: Parameters<T>) => void {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  return useCallback(
    (...args: Parameters<T>) => {
      if (timerRef.current) clearTimeout(timerRef.current)
      timerRef.current = setTimeout(() => fn(...args), delay)
    },
    [fn, delay],
  )
}
