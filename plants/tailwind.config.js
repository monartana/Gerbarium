/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./../templates/**/*.*"],

  theme: {
    extend: {
      boxShadow: {
        who: '0px -2px 2px var(--accent)',
      },
      colors: {
        'text': 'var(--text)',
        'background': 'var(--background)',
        'primary': 'var(--primary)',
        'secondary': 'var(--secondary)',
        'accent': 'var(--accent)',
      },
    },
  },

  plugins: [],
};
