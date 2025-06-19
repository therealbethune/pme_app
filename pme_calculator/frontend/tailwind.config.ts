import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
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
        // Scale.ai-inspired palette
        brand: {
          DEFAULT: "#1877FF",
          50: "#EBF4FF",
          100: "#D6E8FF",
          200: "#B3D4FF",
          300: "#85BDFF",
          400: "#529AFF",
          500: "#1877FF",
          600: "#0052E6",
          700: "#0040B8",
          800: "#003399",
          900: "#002975",
        },
        surface: "#F8F9FB",
        base: {
          DEFAULT: "#0B0C0E",
          50: "#F7F8F9",
          100: "#EDEEF1",
          200: "#D4D6DC",
          300: "#B8BBC5",
          400: "#9CA1AD",
          500: "#7E8491",
          600: "#656B78",
          700: "#4E5562",
          800: "#3A4148",
          900: "#262A32",
          950: "#0B0C0E",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "#00cfff",
          foreground: "hsl(var(--accent-foreground))",
        },
        'accent-soft': "#00cfff1a",
        bg: {
          base: "#0d0d0d",
          raised: "#141414",
          elevated: "#111111"
        },
        fg: {
          primary: "#e5e7eb",
          muted: "#94a3b8"
        },
        text: {
          primary: "#f9fafb",
          muted: "#94a3b8"
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Override default whites
        white: "#e5e7eb",
        gray: {
          50: "#1f2937",
          100: "#374151",
          200: "#4b5563",
          300: "#6b7280",
          400: "#9ca3af",
          500: "#d1d5db",
          600: "#e5e7eb",
          700: "#f3f4f6",
          800: "#f9fafb",
          900: "#ffffff",
        }
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
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
        'spin-slow': {
          to: { transform: 'rotate(360deg)' }
        },
        'pulse-slow': {
          '0%,100%': { opacity: '0.4' },
          '50%': { opacity: '0.8' },
        },
        'glow-pulse': {
          '0%,100%': { boxShadow: '0 0 25px #00cfff55' },
          '50%': { boxShadow: '0 0 35px #00cfff80' },
        },
        'pulse-neon': {
          '0%,100%': { 
            transform: 'scale(1)', 
            boxShadow: '0 0 28px #00cfff33' 
          },
          '50%': { 
            transform: 'scale(1.05)', 
            boxShadow: '0 0 42px #00cfff44' 
          },
        },
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        'spin-slow': 'spin-slow 8s linear infinite',
        'pulse-slow': 'pulse-slow 6s ease-in-out infinite',
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        'pulse-neon': 'pulse-neon 1.2s ease-in-out infinite',
        'fade-in-up': 'fade-in-up 0.5s ease-out',
      },
      fontFamily: {
        sans: ["Inter Variable", "Inter", "system-ui", "sans-serif"],
        inter: ['Inter Variable', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        card: '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)',
        neon: '0 0 28px #00cfff33',
        'neon-lg': '0 0 42px #00cfff44',
        'neon-subtle': '0 0 20px #00cfff1a',
        'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
      },
      backdropBlur: {
        xs: '2px',
      },
      spacing: {
        // 8pt grid system
        '18': '4.5rem',
        '22': '5.5rem',
      },
      borderColor: {
        DEFAULT: 'rgb(148 163 184 / 0.25)',
      },
      ringColor: {
        DEFAULT: 'rgb(148 163 184 / 0.25)',
      },
      divideColor: {
        DEFAULT: 'rgb(148 163 184 / 0.25)',
      }
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config

export default config 