/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ['Fraunces', 'Georgia', 'serif'],
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        dossier: {
          canvas: '#090d14',
          surface: '#111622',
          subtle: '#161d2c',
          border: '#1e2638',
          borderStrong: '#2c3952',
          amber: '#d97706',
          amberLight: '#f59e0b',
          amberBg: '#271704',
          verified: '#10b981',
          verifiedBg: '#052e1f',
          blue: '#3b82f6',
          blueBg: '#0e2246',
          unconfirmed: '#ef4444',
          unconfirmedBg: '#360d0d',
          redacted: '#000000',
        }
      }
    },
  },
  plugins: [],
}
