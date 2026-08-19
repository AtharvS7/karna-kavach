'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { clsx } from 'clsx'
import ThemeToggle from './ThemeToggle'

const NAV = [
  { href: '/',           label: 'Dashboard' },
  { href: '/attacks',    label: 'Attack Library' },
  { href: '/detection',  label: 'Live Detection' },
  { href: '/analytics',  label: 'Analytics' },
]

export default function Navbar() {
  const path = usePathname()
  return (
    <nav className="fixed top-0 inset-x-0 z-50 border-b border-[var(--color-border)] bg-[var(--color-nav-bg)] backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">

        {/* Logo with Mastercard circles */}
        <Link href="/" className="flex items-center gap-3" prefetch={true}>
          <div className="relative w-10 h-6 flex-shrink-0">
            <div className="absolute left-0 top-0 w-6 h-6 rounded-full bg-mc_red opacity-90" />
            <div className="absolute left-4 top-0 w-6 h-6 rounded-full bg-mc_amber opacity-90 mix-blend-multiply dark:mix-blend-screen" />
          </div>
          <span className="font-display text-lg font-bold tracking-tight text-[var(--color-text)]">
            Karna<span className="text-mc_red">·</span>Kavach
          </span>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-1">
          {NAV.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              prefetch={true}
              className={clsx(
                'px-4 py-2 rounded text-sm font-medium transition-all duration-200',
                path === href
                  ? 'bg-mc_red/10 text-mc_red border border-mc_red/20'
                  : 'text-[var(--color-text-50)] hover:text-[var(--color-text)] hover:bg-[var(--color-bg-input)]'
              )}
            >
              {label}
            </Link>
          ))}
        </div>

        {/* Theme toggle + Status pill */}
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <div className="flex items-center gap-2 text-xs font-mono text-emerald-500 dark:text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500 dark:bg-emerald-400 animate-pulse-slow" />
            SYSTEM ACTIVE
          </div>
        </div>
      </div>
    </nav>
  )
}
