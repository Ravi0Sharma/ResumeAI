import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./pages/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./app/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}"],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        "border-light": "hsl(var(--border-light))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        "foreground-muted": "hsl(var(--foreground-muted))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
          glow: "hsl(var(--primary-glow))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        success: {
          DEFAULT: "hsl(var(--success))",
          foreground: "hsl(var(--success-foreground))",
          glow: "hsl(var(--success-glow))",
        },
        warning: {
          DEFAULT: "hsl(var(--warning))",
          foreground: "hsl(var(--warning-foreground))",
          glow: "hsl(var(--warning-glow))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
          glow: "hsl(var(--muted-glow))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        surface: {
          DEFAULT: "hsl(var(--surface))",
          light: "hsl(var(--surface-light))",
        },
      },
      backgroundImage: {
        "gradient-main": "linear-gradient(135deg, hsl(var(--bg-dark)) 0%, hsl(var(--bg-mid)) 50%, hsl(var(--bg-light)) 100%)",
        "gradient-radial": "radial-gradient(ellipse at top, hsl(var(--bg-light)) 0%, hsl(var(--bg-dark)) 70%)",
        "gradient-card": "linear-gradient(145deg, hsl(var(--surface-light)) 0%, hsl(var(--surface)) 100%)",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
      boxShadow: {
        "glow-primary": "0 0 20px -5px hsl(var(--primary-glow) / 0.4)",
        "glow-success": "0 0 20px -5px hsl(var(--success-glow) / 0.4)",
        "glow-warning": "0 0 20px -5px hsl(var(--warning-glow) / 0.4)",
        "glow-muted": "0 0 20px -5px hsl(var(--muted-glow) / 0.4)",
        "card": "0 4px 24px -4px rgba(0, 0, 0, 0.3), inset 0 1px 0 0 hsl(var(--border-light) / 0.1)",
        "card-hover": "0 8px 32px -4px rgba(0, 0, 0, 0.4), inset 0 1px 0 0 hsl(var(--border-light) / 0.15)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config;
