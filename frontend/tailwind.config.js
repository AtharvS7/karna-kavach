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
        ink:    '#141413',
        'ink-2':'#1E1E1C',
        'ink-3':'#2A2A28',
        cream:  '#F5F5F0',
        'cream-2':'#E8E8E3',
        mc_red: '#EB001B',
        mc_amber:'#F79E1B',
        'mc-overlap':'#FF5F00',
      },
      fontFamily: {
        display: ['var(--font-display)', 'Georgia', 'serif'],
        body:    ['var(--font-body)', 'system-ui', 'sans-serif'],
        mono:    ['var(--font-mono)', 'monospace'],
      },
      backgroundImage: {
        'mc-gradient': 'linear-gradient(135deg, #EB001B 0%, #FF5F00 50%, #F79E1B 100%)',
        'dark-mesh':   'radial-gradient(ellipse at 20% 50%, #1E1E1C 0%, #141413 100%)',
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
