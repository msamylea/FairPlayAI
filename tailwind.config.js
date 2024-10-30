module.exports = {
    content: ["./templates/**/*.html", "./static/**/*.js"],
    theme: {
      extend: {
        colors: {
          primary: {
            light: '#696e8e', 
            DEFAULT: '#696e8e',  // Removed extra #
            dark: '#696e8e',     // Removed extra #
          },
          secondary: {
            light: '#96b1be',
            DEFAULT: '#96b1be',
            dark: '#96b1be',
          },
          accent: {
            light: '#a4543e',
            DEFAULT: '#a4543e',
            dark: '#a4543e',
          },
          neutral: {
            50: "#e9e3df",
            100: "#d1cac4",
            200: "#b7b1ac",
            300: "#9e9995",
            400: "#86817e",
            500: "#6f6b68",
            600: "#585552",
            700: "#43403f",
            800: "#2e2c2b",
            900: "#1a1918",
          },
    
        },
        fontFamily: {
          sans: ["Arsenal SC", "sans-serif"],
      },
    },
  },
  plugins: [
    // require('@tailwindcss/typography'),
    // require('@tailwindcss/forms'),
    // require('@tailwindcss/aspect-ratio'),
  ],
};

