// Shourya/tailwind.config.js - Tailwind CSS configuration using authentic ShadCN UI design tokens.
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"], // Toggle dark mode via '.dark' class on <html>
  content: [
    "./index.html", // Scan root HTML template
    "./src/**/*.{ts,tsx}", // Scan all of Shourya's ShadCN UI components
    "../Prakshat/charts/**/*.{ts,tsx}", // Scan Prakshat's React chart components so utility classes are preserved
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"], // Clean UI sans font
        mono: ["JetBrains Mono", "Consolas", "ui-monospace", "monospace"], // Tabular monospace for numbers & tickers
      },
      colors: {
        border: "hsl(var(--border))", // ShadCN border token
        input: "hsl(var(--input))", // ShadCN input border token
        ring: "hsl(var(--ring))", // ShadCN focus ring token
        background: "hsl(var(--background))", // ShadCN page canvas token
        foreground: "hsl(var(--foreground))", // ShadCN primary text token
        primary: {
          DEFAULT: "hsl(var(--primary))", // Primary action fill
          foreground: "hsl(var(--primary-foreground))", // Primary button text
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))", // Secondary surface fill
          foreground: "hsl(var(--secondary-foreground))", // Secondary text
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))", // Loss / error / stop-loss accent
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))", // Subtle muted container fill
          foreground: "hsl(var(--muted-foreground))", // Muted caption text
        },
        accent: {
          DEFAULT: "hsl(var(--accent))", // Hover highlight background
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))", // Select/Command/Tooltip surface
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))", // Elevated ShadCN card surface
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)", // Large card radius
        md: "calc(var(--radius) - 2px)", // Medium input/button radius
        sm: "calc(var(--radius) - 4px)", // Small badge radius
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out", // Smooth Radix accordion expand
        "accordion-up": "accordion-up 0.2s ease-out", // Smooth Radix accordion collapse
      },
    },
  },
  plugins: [require("tailwindcss-animate")], // ShadCN animation utility classes
};
