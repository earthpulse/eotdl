/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js,svelte,ts}"],
  theme: {
    extend: {
      colors: {
        'blue': {
          500: '#003247'
        },
        'green': {
          200: '#4ABFA7'
        }
      }
    },

  },
  plugins: [require("daisyui")]
};
