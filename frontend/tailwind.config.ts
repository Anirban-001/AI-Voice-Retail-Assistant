import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";

const config: Config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["IBM Plex Sans", "sans-serif"]
      },
      colors: {
        primary: {
          DEFAULT: "#1B5F8C",
          foreground: "#F4F4F4"
        },
        accent: {
          DEFAULT: "#F38630",
          foreground: "#1A1C1D"
        }
      }
    }
  },
  plugins: [animate]
};

export default config;
