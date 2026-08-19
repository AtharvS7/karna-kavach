/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        /* Theme-aware via CSS custom properties */
        ink:      'var(--color-bg)',
        'ink-2':  'var(--color-bg-card)',
        'ink-3':  'var(--color-bg-input)',
        cream:    'var(--color-text)',
        'cream-2':'var(--color-text-70)',

        /* Brand colors (constant across themes) */
        mc_red:       '#EB001B',
        mc_amber:     '#F79E1B',
        'mc-overlap': '#FF5F00',
      },
      fontFamily: {
        display: ['var(--font-display)', 'Georgia', 'serif'],
        body:    ['var(--font-body)', 'system-ui', 'sans-serif'],
        mono:    ['var(--font-mono)', 'monospace'],
      },
      backgroundImage: {
        'mc-gradient': 'linear-gradient(135deg, #EB001B 0%, #FF5F00 50%, #F79E1B 100%)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'fade-up':    'fadeUp 0.5s ease-out forwards',
        'scan':       'scan 2s linear infinite',
      },
      keyframes: {
        fadeUp: {
          '0%':   { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scan: {
          '0%':   { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
      },
    },
  },
  plugins: [],
}
