/** @type {import('tailwindcss').Config} */
// index.html'deki eski inline Play CDN config'in birebir taşınmış hali.
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.jsx', './tweaks-panel.jsx'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Manrope', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Poppins', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        accent: {
          DEFAULT: 'var(--accent)',
          soft: 'var(--accent-soft)',
          text: 'var(--accent-text)',
        },
        kcal: 'var(--c-kcal)',
        prot: 'var(--c-prot)',
        carb: 'var(--c-carb)',
        fat: 'var(--c-fat)',
      },
      borderRadius: {
        xl2: '1.25rem',
      },
      boxShadow: {
        soft: '0 1px 2px rgba(16,24,40,0.04), 0 8px 24px -12px rgba(16,24,40,0.12)',
        softlg: '0 2px 4px rgba(16,24,40,0.04), 0 18px 40px -16px rgba(16,24,40,0.18)',
      },
    },
  },
};
