'use client'
import { useState, useEffect } from 'react'
import { predictFraud, generateTransaction } from '@/lib/api'
import { clsx } from 'clsx'

const MERCHANT_CATEGORIES = [
  'retail', 'grocery', 'gas_station', 'restaurant',
  'electronics', 'travel', 'entertainment', 'atm', 'online', 'pharmacy',
]

const SAMPLE_LEGIT = {
  merchant_name: 'Walmart #4821',
  merchant_category: 'grocery',
  amount: 67.43,
  city: 'Austin',
  country: 'US',
  card_present: true,
  velocity_1h: 1,
  amount_deviation: 0.12,
  cross_border: false,
}

const SAMPLE_FRAUD = {
  merchant_name: 'ElectroMax Online',
  merchant_category: 'electronics',
  amount: 1899.00,
  city: 'Lagos',
  country: 'NG',
  card_present: false,
  velocity_1h: 8,
  amount_deviation: 4.7,
  cross_border: true,
}

interface PredictResult {
  is_fraud: boolean
  fraud_probability: number
  risk_score: number
  confidence: string
  top_features: Record<string, unknown>
}

function RiskGauge({ score }: { score: number }) {
  const color = score > 70 ? '#EB001B' : score > 40 ? '#F79E1B' : '#10b981'
  const label = score > 70 ? 'HIGH RISK' : score > 40 ? 'MEDIUM RISK' : 'LOW RISK'
  const angle = (score / 100) * 180 - 90

  // Theme-aware gauge tick color
  const [tickColor, setTickColor] = useState('rgba(255,255,255,0.26)')
  useEffect(() => {
    const check = () => {
      const dark = document.documentElement.classList.contains('dark')
      setTickColor(dark ? 'rgba(255,255,255,0.26)' : 'rgba(26,26,26,0.3)')
    }
    check()
    const observer = new MutationObserver(check)
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => observer.disconnect()
  }, [])

  const trackColor = typeof window !== 'undefined' && !document.documentElement.classList.contains('dark')
    ? '#e0e0dc' : '#2A2A28'

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 200 120" className="w-48 h-28">
        <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke={trackColor} strokeWidth="16" strokeLinecap="round" />
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke={color}
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray={`${(score / 100) * 251.2} 251.2`}
          style={{ transition: 'stroke-dasharray 0.8s ease, stroke 0.4s ease' }}
        />
        <line
          x1="100" y1="100"
          x2={100 + 60 * Math.cos(((angle - 90) * Math.PI) / 180)}
          y2={100 + 60 * Math.sin(((angle - 90) * Math.PI) / 180)}
          stroke={color}
          strokeWidth="3"
          strokeLinecap="round"
          style={{ transition: 'all 0.8s ease' }}
        />
        <circle cx="100" cy="100" r="6" fill={color} />
        <text x="18" y="118" fill={tickColor} fontSize="10" fontFamily="monospace">0</text>
        <text x="178" y="118" fill={tickColor} fontSize="10" fontFamily="monospace">100</text>
      </svg>
      <div className="metric-number text-5xl font-bold mt-1" style={{ color }}>
        {score}
      </div>
      <div className="text-xs font-mono mt-1" style={{ color }}>{label}</div>
    </div>
  )
}

export default function DetectionPage() {
  const [form, setForm] = useState({ ...SAMPLE_LEGIT })
  const [result, setResult] = useState<PredictResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox'
        ? (e.target as HTMLInputElement).checked
        : type === 'number' ? parseFloat(value) || 0 : value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await predictFraud(form)
      setResult(res)
    } catch (err) {
      setError('Backend unavailable. Run: cd backend && uvicorn api.main:app --reload')
    } finally {
      setLoading(false)
    }
  }

  const loadSample = (isFraud: boolean) => {
    setForm({ ...(isFraud ? SAMPLE_FRAUD : SAMPLE_LEGIT) })
    setResult(null)
  }

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const txn = await generateTransaction()
      setForm({
        merchant_name: txn.merchant_name,
        merchant_category: txn.merchant_category,
        amount: txn.amount,
        city: txn.city,
        country: txn.country,
        card_present: txn.card_present ?? true,
        velocity_1h: txn.velocity_1h ?? 1,
        amount_deviation: txn.amount_deviation ?? 0,
        cross_border: txn.cross_border ?? false,
      })
      setResult(null)
    } catch {
      setError('Could not generate transaction — check backend')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-ink noise-bg">
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-10 animate-fade-up">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-mc_amber/30 bg-mc_amber/10 text-mc_amber text-xs font-mono mb-4">
            PILLAR 03 · DEFEND ENGINE
          </div>
          <h1 className="font-display text-4xl font-black text-[var(--color-text)] mb-3">Live Detection</h1>
          <p className="text-[var(--color-text-50)]">
            Submit a transaction and get a real-time fraud risk score from the trained ensemble classifier.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Form */}
          <div className="bg-ink-2 border border-ink-3 rounded-2xl p-8 animate-fade-up delay-100">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-[var(--color-text)] font-semibold text-lg">Transaction Details</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => loadSample(false)}
                  className="px-3 py-1.5 text-xs font-mono border border-emerald-500/30 text-emerald-500 rounded hover:bg-emerald-500/10 transition-colors"
                >
                  Load Legit
                </button>
                <button
                  onClick={() => loadSample(true)}
                  className="px-3 py-1.5 text-xs font-mono border border-mc_red/30 text-mc_red rounded hover:bg-mc_red/10 transition-colors"
                >
                  Load Fraud
                </button>
                <button
                  onClick={handleGenerate}
                  className="px-3 py-1.5 text-xs font-mono border border-mc_amber/30 text-mc_amber rounded hover:bg-mc_amber/10 transition-colors"
                >
                  ⟳ Generate
                </button>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-mono text-[var(--color-text-40)] uppercase tracking-widest block mb-1.5">
                    Merchant Name
                  </label>
                  <input
                    name="merchant_name"
                    value={form.merchant_name}
                    onChange={handleChange}
                    className="w-full bg-ink-3 border border-ink-3 rounded-lg px-3 py-2.5 text-sm text-[var(--color-text)] focus:outline-none focus:border-mc_red/40"
                  />
                </div>
                <div>
                  <label className="text-xs font-mono text-[var(--color-text-40)] uppercase tracking-widest block mb-1.5">
                    Category
                  </label>
                  <select
                    name="merchant_category"
                    value={form.merchant_category}
                    onChange={handleChange}
                    className="w-full bg-ink-3 border border-ink-3 rounded-lg px-3 py-2.5 text-sm text-[var(--color-text)] focus:outline-none focus:border-mc_red/40"
                  >
                    {MERCHANT_CATEGORIES.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-mono text-[var(--color-text-40)] uppercase tracking-widest block mb-1.5">
                    Amount (USD)
                  </label>
                  <input
                    name="amount" type="number" step="0.01"
                    value={form.amount}
                    onChange={handleChange}
                    className="w-full bg-ink-3 border border-ink-3 rounded-lg px-3 py-2.5 text-sm text-[var(--color-text)] focus:outline-none focus:border-mc_red/40"
                  />
                </div>
                <div>
                  <label className="text-xs font-mono text-[var(--color-text-40)] uppercase tracking-widest block mb-1.5">
                    Country
                  </label>
                  <input
                    name="country"
                    value={form.country}
                    onChange={handleChange}
                    className="w-full bg-ink-3 border border-ink-3 rounded-lg px-3 py-2.5 text-sm text-[var(--color-text)] focus:outline-none focus:border-mc_red/40"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="text-xs font-mono text-[var(--color-text-40)] uppercase tracking-widest block mb-1.5">
                    Velocity (1h)
                  </label>
                  <input
                    name="velocity_1h" type="number"
                    value={form.velocity_1h}
                    onChange={handleChange}
                    className="w-full bg-ink-3 border border-ink-3 rounded-lg px-3 py-2.5 text-sm text-[var(--color-text)] focus:outline-none focus:border-mc_red/40"
                  />
                </div>
                <div>
                  <label className="text-xs font-mono text-[var(--color-text-40)] uppercase tracking-widest block mb-1.5">
                    Amt Deviation
                  </label>
                  <input
                    name="amount_deviation" type="number" step="0.01"
                    value={form.amount_deviation}
                    onChange={handleChange}
                    className="w-full bg-ink-3 border border-ink-3 rounded-lg px-3 py-2.5 text-sm text-[var(--color-text)] focus:outline-none focus:border-mc_red/40"
                  />
                </div>
                <div className="flex flex-col justify-end pb-1">
                  <label className="text-xs font-mono text-[var(--color-text-40)] uppercase tracking-widest block mb-1.5">
                    Cross-Border
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox" name="cross_border"
                      checked={form.cross_border}
                      onChange={handleChange}
                      className="w-4 h-4 accent-mc_red"
                    />
                    <span className="text-sm text-[var(--color-text-60)]">Yes</span>
                  </label>
                </div>
              </div>

              {error && (
                <p className="text-xs font-mono text-mc_red bg-mc_red/10 border border-mc_red/20 rounded-lg p-3">
                  ⚠ {error}
                </p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-mc_red text-white font-semibold text-sm rounded-lg hover:bg-mc_red/90 disabled:opacity-50 transition-colors scan-overlay"
              >
                {loading ? 'Analyzing…' : 'Analyze Transaction'}
              </button>
            </form>
          </div>

          {/* Result */}
          <div className="bg-ink-2 border border-ink-3 rounded-2xl p-8 flex flex-col animate-fade-up delay-200">
            <h2 className="text-[var(--color-text)] font-semibold text-lg mb-6">Detection Result</h2>

            {!result && !loading && (
              <div className="flex-1 flex flex-col items-center justify-center text-[var(--color-text-30)]">
                <div className="w-16 h-16 rounded-full border-2 border-dashed border-ink-3 flex items-center justify-center mb-4">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <p className="text-sm font-mono">Submit a transaction to see results</p>
              </div>
            )}

            {loading && (
              <div className="flex-1 flex flex-col items-center justify-center gap-4">
                <div className="w-16 h-16 rounded-full border-2 border-mc_red/30 border-t-mc_red animate-spin" />
                <p className="text-sm font-mono text-[var(--color-text-40)]">Running ensemble classifier…</p>
              </div>
            )}

            {result && (
              <div className="flex-1 flex flex-col items-center gap-6">
                <RiskGauge score={result.risk_score} />

                <div className={clsx(
                  'w-full rounded-xl p-4 text-center border',
                  result.is_fraud
                    ? 'bg-mc_red/10 border-mc_red/30'
                    : 'bg-emerald-500/10 border-emerald-500/30'
                )}>
                  <div className={clsx(
                    'text-2xl font-display font-bold mb-1',
                    result.is_fraud ? 'text-mc_red' : 'text-emerald-500'
                  )}>
                    {result.is_fraud ? '⚠ FRAUD DETECTED' : '✓ LEGITIMATE'}
                  </div>
                  <div className="text-xs font-mono text-[var(--color-text-50)]">
                    {(result.fraud_probability * 100).toFixed(1)}% probability · {result.confidence} confidence
                  </div>
                </div>

                <div className="w-full">
                  <h4 className="text-xs font-mono text-[var(--color-text-40)] uppercase tracking-widest mb-3">
                    Top Risk Signals
                  </h4>
                  <div className="space-y-2">
                    {Object.entries(result.top_features).map(([k, v]) => {
                      const val = typeof v === 'number' ? v : 0
                      return (
                        <div key={k} className="flex items-center gap-3">
                          <span className="font-mono text-xs text-[var(--color-text-40)] w-36 flex-shrink-0">{k}</span>
                          <div className="flex-1 bg-ink-3 rounded-full h-1.5 overflow-hidden">
                            <div
                              className="h-full bg-mc_red/70 rounded-full transition-all duration-700"
                              style={{ width: `${Math.min(100, val * 100)}%` }}
                            />
                          </div>
                          <span className="font-mono text-xs text-[var(--color-text-60)] w-12 text-right">
                            {typeof v === 'number' ? v.toFixed(2) : String(v)}
                          </span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
