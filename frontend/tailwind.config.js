/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        phishing: '#ef4444',
        suspicious: '#f59e0b',
        legitimate: '#22c55e',
      },
    },
  },
  plugins: [],
}
