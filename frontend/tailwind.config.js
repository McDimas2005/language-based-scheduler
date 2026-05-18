/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17201b",
        moss: "#375a45",
        mint: "#dff5e9",
        coral: "#f6785c",
        sky: "#c8e8ff",
        paper: "#f7f4ee",
        graphite: "#29302c",
      },
      boxShadow: {
        soft: "0 18px 60px rgba(23, 32, 27, 0.14)",
        line: "inset 0 0 0 1px rgba(23, 32, 27, 0.1)",
      },
    },
  },
  plugins: [],
};

