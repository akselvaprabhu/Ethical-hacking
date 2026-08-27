/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: '#0a0d14',
          card: '#121824',
          border: '#1e293b',
          accent: '#00f0ff',
          neon: '#00ff88',
          warning: '#ffb703',
          danger: '#ff0055',
          muted: '#64748b'
        }
      }
    },
  },
  plugins: [],
}
