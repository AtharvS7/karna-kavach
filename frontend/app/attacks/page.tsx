'use client'
import { useEffect, useState } from 'react'
import { fetchAttacks, fetchCategories } from '@/lib/api'
import { clsx } from 'clsx'

interface Attack {
  id: number
  attack_id: string
  name: string
  category: string
  genai_amplification: string
  attack_steps: string[]
  target_channel: string
  detection_challenges: string[]
  transaction_features: Record<string, unknown>
}

const CATEGORY_COLORS: Record<string, string> = {
  'Card-Not-Present Fraud': 'text-mc_red border-mc_red/30 bg-mc_red/10',
  'Social Engineering':     'text-orange-400 border-orange-400/30 bg-orange-400/10',
  'Account Takeover':       'text-mc_amber border-mc_amber/30 bg-mc_amber/10',
  'Synthetic Identity Fraud':'text-sky-400 border-sky-400/30 bg-sky-400/10',
  'Authorization Bypass':   'text-violet-400 border-violet-400/30 bg-violet-400/10',
  'Merchant & Refund Fraud':'text-emerald-400 border-emerald-400/30 bg-emerald-400/10',
}

function AttackCard({ attack, onClick }: { attack: Attack; onClick: () => void }) {
  const color = CATEGORY_COLORS[attack.category] ?? 'text-cream/60 border-cream/20 bg-cream/5'
  return (
    <button
      onClick={onClick}
      className="w-full text-left bg-ink-2 border border-ink-3 rounded-xl p-6 card-glow hover:border-mc_red/30 transition-all"
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <span className={clsx('text-xs font-mono px-2 py-1 rounded-full border', color)}>
          {attack.category}
        </span>
        <span className="text-xs font-mono text-cream/30">{attack.attack_id}</span>
      </div>
      <h3 className="font-display text-lg font-bold text-cream mb-2 leading-snug">
        {attack.name}
      </h3>
      <p className="text-cream/50 text-sm leading-relaxed line-clamp-2">
        {attack.genai_amplification}
      </p>
      <div className="mt-4 flex items-center gap-2 text-xs text-cream/30">
        <span className="font-mono">📡 {attack.target_channel}</span>
        <span>·</span>
        <span>{attack.attack_steps?.length ?? 0} steps</span>
      </div>
    </button>
  )
}

function AttackModal({ attack, onClose }: { attack: Attack; onClose: () => void }) {
  const color = CATEGORY_COLORS[attack.category] ?? 'text-cream/60 border-cream/20 bg-cream/5'
  const tf = attack.transaction_features

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-ink/80 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-ink-2 border border-ink-3 rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-8 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between mb-6">
          <div>
            <span className={clsx('text-xs font-mono px-2 py-1 rounded-full border', color)}>
              {attack.category}
            </span>
            <h2 className="font-display text-2xl font-bold text-cream mt-3">
              {attack.name}
            </h2>
            <p className="text-xs font-mono text-cream/30 mt-1">{attack.attack_id}</p>
          </div>
          <button
            onClick={onClose}
            className="text-cream/30 hover:text-cream text-2xl leading-none flex-shrink-0"
          >
            ×
          </button>
        </div>

        <div className="space-y-6">
          <div>
            <h4 className="text-xs font-mono text-mc_red uppercase tracking-widest mb-2">
              GenAI Amplification
            </h4>
            <p className="text-cream/70 text-sm leading-relaxed bg-mc_red/5 border border-mc_red/10 rounded-lg p-4">
              {attack.genai_amplification}
            </p>
          </div>

          <div>
            <h4 className="text-xs font-mono text-mc_amber uppercase tracking-widest mb-2">
              Attack Steps
            </h4>
            <ol className="space-y-2">
              {attack.attack_steps?.map((step, i) => (
                <li key={i} className="flex gap-3 text-sm text-cream/70">
                  <span className="font-mono text-mc_amber flex-shrink-0">{String(i + 1).padStart(2, '0')}</span>
                  {step}
                </li>
              ))}
            </ol>
          </div>

          <div>
            <h4 className="text-xs font-mono text-sky-400 uppercase tracking-widest mb-2">
              Detection Challenges
            </h4>
            <ul className="space-y-2">
              {attack.detection_challenges?.map((c, i) => (
                <li key={i} className="flex gap-2 text-sm text-cream/70">
                  <span className="text-sky-400 mt-0.5">⚠</span>
                  {c}
                </li>
              ))}
            </ul>
          </div>

          {tf && (
            <div>
              <h4 className="text-xs font-mono text-emerald-400 uppercase tracking-widest mb-3">
                Transaction Feature Signatures
              </h4>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(tf).map(([k, v]) => (
                  <div key={k} className="bg-ink-3 rounded-lg p-3 flex justify-between items-center text-xs">
                    <span className="font-mono text-cream/40">{k}</span>
                    <span className="font-mono text-emerald-400">
                      {Array.isArray(v) ? `[${v.join(', ')}]` : String(v)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function AttacksPage() {
  const [attacks, setAttacks] = useState<Attack[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [active, setActive] = useState<string>('')
  const [selected, setSelected] = useState<Attack | null>(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    Promise.all([fetchAttacks(), fetchCategories()]).then(([a, c]) => {
      setAttacks(a)
      setCategories(c)
      setLoading(false)
    })
  }, [])

  const filtered = attacks.filter((a) => {
    const matchCat = !active || a.category === active
    const matchSearch = !search || a.name.toLowerCase().includes(search.toLowerCase()) ||
      a.genai_amplification.toLowerCase().includes(search.toLowerCase())
    return matchCat && matchSearch
  })

  return (
    <div className="min-h-screen bg-ink noise-bg">
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-10 animate-fade-up">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-mc_red/30 bg-mc_red/10 text-mc_red text-xs font-mono mb-4">
            PILLAR 01 · IDENTIFY ENGINE
          </div>
          <h1 className="font-display text-4xl font-black text-cream mb-3">
            Attack Library
          </h1>
          <p className="text-cream/50 max-w-xl">
            {attacks.length} GenAI-amplified payment fraud attack vectors across {categories.length} categories,
            discovered and documented by the Identify Engine.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-8 animate-fade-up delay-100">
          <input
            type="text"
            placeholder="Search attacks…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-ink-2 border border-ink-3 rounded-lg px-4 py-2.5 text-sm text-cream placeholder-cream/30 focus:outline-none focus:border-mc_red/40"
          />
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setActive('')}
              className={clsx(
                'px-3 py-1.5 rounded-lg text-xs font-mono border transition-colors',
                !active ? 'bg-mc_red/10 border-mc_red/30 text-mc_red' : 'border-ink-3 text-cream/50 hover:text-cream'
              )}
            >
              All ({attacks.length})
            </button>
            {categories.map((cat) => {
              const color = CATEGORY_COLORS[cat] ?? 'text-cream/60 border-cream/20'
              return (
                <button
                  key={cat}
                  onClick={() => setActive(cat === active ? '' : cat)}
                  className={clsx(
                    'px-3 py-1.5 rounded-lg text-xs font-mono border transition-colors',
                    active === cat ? color : 'border-ink-3 text-cream/50 hover:text-cream'
                  )}
                >
                  {cat.split(' ')[0]}
                </button>
              )
            })}
          </div>
        </div>

        {/* Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(9)].map((_, i) => (
              <div key={i} className="bg-ink-2 border border-ink-3 rounded-xl h-48 animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((attack, i) => (
              <div
                key={attack.attack_id}
                className="animate-fade-up"
                style={{ animationDelay: `${i * 0.04}s`, opacity: 0 }}
              >
                <AttackCard attack={attack} onClick={() => setSelected(attack)} />
              </div>
            ))}
          </div>
        )}

        {!loading && filtered.length === 0 && (
          <div className="text-center py-20 text-cream/30">
            <div className="text-4xl mb-4">🔍</div>
            <p className="font-mono text-sm">No attacks match your filters.</p>
            <p className="text-xs mt-2">The Identify Engine may still be generating the taxonomy. Run <code className="text-mc_red">python pipeline.py --identify</code></p>
          </div>
        )}
      </div>

      {selected && <AttackModal attack={selected} onClose={() => setSelected(null)} />}
    </div>
  )
}
