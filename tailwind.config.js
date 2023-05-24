/** @type {import('tailwindcss').Config} */
const path = require('path')

module.exports = {
  content: [
      "./build/**/*.html",
      "./node_modules/preline/dist/*.js",
  ],

  darkMode: "media", // or 'false' or 'class'
  theme: {
    extend: {},
  },
  plugins: [
    require('preline/plugin'),
  ],
}

