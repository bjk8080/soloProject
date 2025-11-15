/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],

  theme: {
    extend: {
      keyframes: {
        cardFan: {
          "0%": {
            transform: "translate(0,0) rotate(0deg)",
            opacity: "0",
          },
          "100%": {
            transform: "translate(var(--x-offset), 0) rotate(var(--rotate))",
            opacity: "1",
          },
        },
      },
      animation: {
        cardFan: "cardFan 0.6s ease-out forwards",
      },
    },
  },

  safelist: [
    "animate-cardFan",
  ],

  plugins: [],
};
