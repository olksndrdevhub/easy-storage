/** @type {import('tailwindcss').Config} */
const colors = require("tailwindcss/colors");
module.exports = {
  content: ["./templates/**/*.{html,js}", "./**/templates/**/*.{html,js}"],
  theme: {
    extend: {},
    colors: {
      transparent: "transparent",
      current: "currentColor",
      white: "#ffffff",
      primary: "#000",
      secondary: "#950A00",
      base: "#F0F0F0",
      neutral: "#313131",
      success: colors.green[500],
      warning: colors.yellow[500],
      error: colors.red[500],
      info: colors.blue[400],
    },
  },
  plugins: [],
};
