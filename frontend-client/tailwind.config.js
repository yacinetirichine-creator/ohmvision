/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Deep futuristic background
        dark: {
          950: '#050a10', // Deepest space - Main BG
          900: '#0a0f16', // Secondary BG
          850: '#111822', // Card bg
          800: '#1a2230',
          700: '#232d3f',
          600: '#2a3441',
          500: '#2d3848',
        },
        // OhmTronic Brand Colors - Futuristic
        ohm: {
          cyan: '#00f0ff', // Cyberpunk Cyan - Primary Brand
          blue: '#0070f3', // Electric Blue
          purple: '#bc13fe', // Neon Purple
          neon: '#39ff14', // Matrix Green (accents)
        },
        primary: {
          DEFAULT: '#00f0ff', // Shift to Cyan as primary for futuristic look
          light: '#60a5fa',
          dark: '#0070f3',
          hover: '#00c2cf',
          dim: 'rgba(0, 240, 255, 0.1)',
        },
        success: '#22c55e',
        warning: '#f59e0b',
        danger: '#ef4444',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'], // Tech feel for data
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'hero-glow': 'conic-gradient(from 180deg at 50% 50%, #1a2230 0deg, #050a10 360deg)',
         'cyber-grid': "url(\"data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h40v40H0V0zm1 1h38v38H1V1z' fill='%2300f0ff' fill-opacity='0.03' fill-rule='evenodd'/%3E%3C/svg%3E\")",
      },
      boxShadow: {
        'neon': '0 0 5px theme("colors.ohm.cyan"), 0 0 20px theme("colors.ohm.cyan")',
        'neon-purple': '0 0 5px theme("colors.ohm.purple"), 0 0 20px theme("colors.ohm.purple")',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      },
      animation: {
        'glow-pulse': 'glow-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        'glow-pulse': {
          '0%, 100%': { opacity: 1, boxShadow: '0 0 5px #00f0ff, 0 0 10px #00f0ff' },
          '50%': { opacity: 0.8, boxShadow: '0 0 2px #00f0ff, 0 0 5px #00f0ff' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        }
      }
    },
  },
  plugins: [],
}
