'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { clsx } from 'clsx'

const NAV = [
  { href: '/',           label: 'Dashboard' },
  { href: '/attacks',    label: 'Attack Library' },
  { href: '/detection',  label: 'Live Detection' },
  { href: '/analytics',  label: 'Analytics' },
]

export default function Navbar() {
  const path = usePathname()
  return (
    <nav className="fixed top-0 inset-x-0 z-50 border-b border-ink-3 bg-ink/95 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">

        {/* Logo with Mastercard circles */}
        <Link href="/" className="flex items-center gap-3">
          <div className="relative w-10 h-6 flex-shrink-0">
            <div className="absolute left-0 top-0 w-6 h-6 rounded-full bg-mc_red opacity-90" />
            <div className="absolute left-4 top-0 w-6 h-6 rounded-full bg-mc_amber opacity-90 mix-blend-screen" />
          </div>
          <span className="font-display text-lg font-bold tracking-tight text-cream">
            Karna<span className="text-mc_red">·</span>Kavach
          </span>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-1">
          {NAV.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={clsx(
                'px-4 py-2 rounded text-sm font-medium transition-all duration-200',
                path === href
                  ? 'bg-mc_red/10 text-mc_red border border-mc_red/20'
                  : 'text-cream/60 hover:text-cream hover:bg-ink-3'
              )}
            >
              {label}
            </Link>
          ))}
        </div>

        {/* Status pill */}
        <div className="flex items-center gap-2 text-xs font-mono text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-slow" />
          SYSTEM ACTIVE
        </div>
      </div>
    </nav>
  )
}
