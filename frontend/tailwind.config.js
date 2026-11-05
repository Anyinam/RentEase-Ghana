/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#152720',
        forest: '#174d3b',
        lime: '#d8f36a',
        muted: '#68756e',
        canvas: '#f7f8f5',
      },
      fontFamily: { sans: ['Inter', 'ui-sans-serif', 'system-ui'] },
      boxShadow: { card: '0 12px 40px rgba(21, 39, 32, 0.07)' },
    },
  },
  plugins: [],
}
