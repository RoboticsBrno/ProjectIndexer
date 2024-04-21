/** @type {import('tailwindcss').Config} */
const path = require('path')

module.exports = {
  content: [
      "./build/**/*.html",
      "./build/assets/css/github-markdown.css",
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

