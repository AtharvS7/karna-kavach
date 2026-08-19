'use client'
import { useEffect, useState } from 'react'

export default function ThemeToggle() {
  const [dark, setDark] = useState(true)

  useEffect(() => {
    // Check localStorage or default to dark
    const saved = localStorage.getItem('kk-theme')
    if (saved === 'light') {
      setDark(false)
      document.documentElement.classList.remove('dark')
    } else {
      setDark(true)
      document.documentElement.classList.add('dark')
    }
  }, [])

  const toggle = () => {
    const next = !dark
    setDark(next)
    if (next) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('kk-theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('kk-theme', 'light')
    }
  }

  return (
    <button
      onClick={toggle}
      aria-label="Toggle theme"
      className="relative w-14 h-7 rounded-full bg-ink-3 dark:bg-ink-3 border border-ink-3 dark:border-ink-3 transition-colors duration-300 flex items-center px-1 group hover:border-mc_red/30"
    >
      {/* Sun icon */}
      <span className={`absolute left-1.5 text-xs transition-opacity duration-300 ${dark ? 'opacity-30' : 'opacity-100'}`}>
        ☀️
      </span>
      {/* Moon icon */}
      <span className={`absolute right-1.5 text-xs transition-opacity duration-300 ${dark ? 'opacity-100' : 'opacity-30'}`}>
        🌙
      </span>
      {/* Slider dot */}
      <span
        className={`w-5 h-5 rounded-full bg-mc_red shadow-md transform transition-transform duration-300 ${
          dark ? 'translate-x-7' : 'translate-x-0'
        }`}
      />
    </button>
  )
}
