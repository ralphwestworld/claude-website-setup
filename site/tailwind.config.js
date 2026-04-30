/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Instrument Serif"', 'ui-serif', 'Georgia', 'serif'],
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        ink: '#0c0d0a',
        bone: '#f4f1ea',
        moss: '#3a4a32',
        rust: '#b5532a',
        stone: '#8a8377',
      },
    },
  },
  plugins: [],
}
