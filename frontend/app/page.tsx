import Link from 'next/link'
import { fetchMetrics } from '@/lib/api'

const STAT_MOCK = [
  { label: 'Attack Vectors Identified', value: '31', unit: 'unique', color: 'text-mc_red' },
  { label: 'Synthetic Transactions', value: '15,000+', unit: 'generated', color: 'text-mc_amber' },
  { label: 'Model Precision', value: '95.2%', unit: 'target', color: 'text-emerald-400' },
  { label: 'Adversarial Iterations', value: '10', unit: 'feedback loops', color: 'text-sky-400' },
]

const PILLARS = [
  {
    num: '01',
    title: 'Identify',
    desc: 'LLM-powered research surfaces 31 distinct GenAI-amplified fraud vectors across 6 attack categories — deepfakes, synthetic identities, voice cloning, and more.',
    href: '/attacks',
    cta: 'View Attack Library →',
    accent: '#EB001B',
  },
  {
    num: '02',
    title: 'Generate',
    desc: 'Faker + rule-based injection engine produces 15,000 synthetic transactions with realistic distributions, velocity spikes, and geographic anomalies per attack profile.',
    href: '/detection',
    cta: 'Try Live Generation →',
    accent: '#FF5F00',
  },
  {
    num: '03',
    title: 'Defend',
    desc: 'XGBoost + Random Forest + Logistic Regression voting ensemble trained on SMOTE-balanced data, with a 10-iteration adversarial loop that strengthens detection over time.',
    href: '/analytics',
    cta: 'View Model Analytics →',
    accent: '#F79E1B',
  },
]

export default async function DashboardPage() {
  const metrics = await fetchMetrics().catch(() => null)

  return (
    <div className="min-h-screen bg-ink noise-bg">
      {/* Hero */}
      <section className="relative max-w-7xl mx-auto px-6 pt-20 pb-16 overflow-hidden">
        {/* Background decorative circles */}
        <div className="absolute -right-32 top-0 w-[600px] h-[600px] rounded-full bg-mc_red/5 blur-3xl pointer-events-none" />
        <div className="absolute -right-8 top-12 w-[400px] h-[400px] rounded-full bg-mc_amber/5 blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-mc_red/30 bg-mc_red/10 text-mc_red text-xs font-mono mb-6 animate-fade-up">
            <span className="w-1.5 h-1.5 rounded-full bg-mc_red animate-pulse" />
            MASTERCARD INNOVATION CHALLENGE 2026 · GFF MUMBAI
          </div>

          <h1 className="font-display text-5xl md:text-7xl font-black text-cream leading-[1.05] mb-6 animate-fade-up delay-100">
            The Armor That
            <br />
            <span className="relative inline-block">
              <span className="relative z-10 bg-mc-gradient bg-clip-text text-transparent">
                Learns to Attack
              </span>
            </span>
          </h1>

          <p className="text-cream/60 text-lg leading-relaxed mb-10 max-w-xl animate-fade-up delay-200">
            Karna Kavach is a closed-loop adversarial AI system that identifies
            emerging GenAI-powered payment fraud, simulates it at scale, and
            defends against it — each attack making the armor stronger.
          </p>

          <div className="flex items-center gap-4 animate-fade-up delay-300">
            <Link
              href="/detection"
              className="px-6 py-3 bg-mc_red text-white font-semibold text-sm rounded hover:bg-mc_red/90 transition-colors"
            >
              Try Live Detection
            </Link>
            <Link
              href="/attacks"
              className="px-6 py-3 border border-cream/20 text-cream/80 font-semibold text-sm rounded hover:border-cream/40 hover:text-cream transition-colors"
            >
              Explore Attack Library
            </Link>
          </div>
        </div>
      </section>

      {/* Stats row */}
      <section className="max-w-7xl mx-auto px-6 pb-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {STAT_MOCK.map((s, i) => (
            <div
              key={s.label}
              className="bg-ink-2 border border-ink-3 rounded-xl p-6 card-glow animate-fade-up"
              style={{ animationDelay: `${i * 0.08}s`, opacity: 0 }}
            >
              <div className={`metric-number text-4xl font-bold mb-1 ${s.color}`}>
                {metrics && s.label.includes('Precision')
                  ? `${(metrics.precision * 100).toFixed(1)}%`
                  : s.value}
              </div>
              <div className="text-cream/40 text-xs uppercase tracking-widest">{s.unit}</div>
              <div className="text-cream/70 text-sm mt-2">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Three pillars */}
      <section className="max-w-7xl mx-auto px-6 pb-24">
        <div className="mb-10">
          <h2 className="font-display text-3xl font-bold text-cream mb-2">
            The Three Pillars
          </h2>
          <p className="text-cream/50 text-sm">
            A closed feedback loop — each pillar feeds the next.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {PILLARS.map((p, i) => (
            <div
              key={p.num}
              className="group bg-ink-2 border border-ink-3 rounded-2xl p-8 card-glow flex flex-col animate-fade-up"
              style={{ animationDelay: `${i * 0.12}s`, opacity: 0 }}
            >
              <div
                className="font-mono text-6xl font-black mb-6 leading-none"
                style={{ color: p.accent + '33' }}
              >
                {p.num}
              </div>
              <h3
                className="font-display text-2xl font-bold mb-4"
                style={{ color: p.accent }}
              >
                {p.title}
              </h3>
              <p className="text-cream/60 text-sm leading-relaxed flex-1 mb-6">
                {p.desc}
              </p>
              <Link
                href={p.href}
                className="text-sm font-semibold transition-colors"
                style={{ color: p.accent }}
              >
                {p.cta}
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* Deadline banner */}
      <section className="max-w-7xl mx-auto px-6 pb-16">
        <div className="bg-gradient-to-r from-mc_red/10 via-ink-2 to-mc_amber/10 border border-mc_red/20 rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <div className="text-xs font-mono text-mc_red uppercase tracking-widest mb-2">Submission Deadline</div>
            <div className="font-display text-3xl font-bold text-cream">August 31, 2026</div>
            <div className="text-cream/50 text-sm mt-1">11:59 PM GMT+5:30 · Kaggle Writeups</div>
          </div>
          <div className="text-right">
            <div className="text-xs font-mono text-cream/40 uppercase tracking-widest mb-2">GFF 2026 Presentation</div>
            <div className="font-display text-xl font-bold text-cream">Sep 8–11, Mumbai</div>
            <div className="text-cream/50 text-sm mt-1">Jio World Centre</div>
          </div>
          <div className="text-right">
            <div className="text-xs font-mono text-mc_amber uppercase tracking-widest mb-2">Total Prize Pool</div>
            <div className="font-display text-3xl font-bold bg-mc-gradient bg-clip-text text-transparent">
              ₹4,48,000
            </div>
            <div className="text-cream/50 text-sm mt-1">~$4,707 USD</div>
          </div>
        </div>
      </section>
    </div>
  )
}
