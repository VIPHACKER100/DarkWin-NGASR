/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkwin: {
          dark: '#0B0F19',
          card: '#1A2234',
          accent: '#00F0FF',
          danger: '#FF003C',
          warning: '#FFAA00',
          success: '#00FF66'
        }
      }
    },
  },
  plugins: [],
}
