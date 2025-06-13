# PME Calculator Migration - Complete File Set

## Frontend Components (Continued)

```typescript
// frontend/src/components/NavTimeline.tsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';

interface NavTimelineProps {
  data: Array<{
    date: string;
    nav: number;
    cumulative_nav: number;
    benchmark_nav?: number;
  }>;
  loading: boolean;
}

const NavTimeline: React.FC<NavTimelineProps> = ({ data, loading }) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short'
    });
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          NAV Timeline
        </h3>
        <div className="text-center text-gray-500 dark:text-gray-400 py-8">
          No NAV data available
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        NAV Timeline
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis 
            dataKey="date" 
            tickFormatter={formatDate}
            className="text-sm text-gray-600 dark:text-gray-400"
          />
          <YAxis 
            tickFormatter={formatCurrency}
            className="text-sm text-gray-600 dark:text-gray-400"
          />
          <Tooltip 
            formatter={(value: number, name: string) => [
              formatCurrency(value), 
              name === 'nav' ? 'Fund NAV' : name === 'benchmark_nav' ? 'Benchmark NAV' : 'Cumulative NAV'
            ]}
            labelFormatter={(label: string) => `Date: ${formatDate(label)}`}
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #ccc',
              borderRadius: '6px',
            }}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="cumulative_nav"
            stroke="#3B82F6"
            fill="#3B82F6"
            fillOpacity={0.3}
            name="Cumulative NAV"
          />
          <Line
            type="monotone"
            dataKey="nav"
            stroke="#EF4444"
            strokeWidth={2}
            dot={{ fill: '#EF4444', strokeWidth: 2, r: 3 }}
            name="Fund NAV"
          />
          {data[0]?.benchmark_nav && (
            <Line
              type="monotone"
              dataKey="benchmark_nav"
              stroke="#10B981"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ fill: '#10B981', strokeWidth: 2, r: 3 }}
              name="Benchmark NAV"
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default NavTimeline;
```

```tsx
// frontend/src/pages/Dashboard.tsx
import React, { useState, useCallback } from 'react';
import { Moon, Sun, Upload, BarChart3, TrendingUp, DollarSign } from 'lucide-react';
import KpiCard from '../components/KpiCard';
import CashflowChart from '../components/CashflowChart';
import NavTimeline from '../components/NavTimeline';
import FileDrop from '../components/FileDrop';

// Types
interface AnalysisResults {
  metrics: {
    irr: number;
    tvpi: number;
    dpi: number;
    rvpi: number;
    pme: number;
    alpha: number;
  };
  cashflow_data: Array<{
    date: string;
    contributions: number;
    distributions: number;
    net_cashflow: number;
  }>;
  nav_data: Array<{
    date: string;
    nav: number;
    cumulative_nav: number;
    benchmark_nav?: number;
  }>;
}

const Dashboard: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Toggle dark mode
  const toggleDarkMode = useCallback(() => {
    setDarkMode(prev => {
      const newMode = !prev;
      if (newMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      return newMode;
    });
  }, []);

  // Handle analysis completion
  const handleAnalysisComplete = useCallback(async (fundFile: File, indexFile: File | null) => {
    setLoading(true);
    setError(null);
    
    try {
      // Call pywebview API
      if (window.pywebview && window.pywebview.api) {
        const results = await window.pywebview.api.run_full_analysis(
          fundFile.path || fundFile.name,
          indexFile?.path || indexFile?.name || null
        );
        
        if (results.success) {
          setAnalysisResults(results.data);
        } else {
          setError(results.error || 'Analysis failed');
        }
      } else {
        // Fallback for development/testing
        console.warn('pywebview API not available, using mock data');
        setAnalysisResults({
          metrics: {
            irr: 0.15,
            tvpi: 2.5,
            dpi: 1.8,
            rvpi: 0.7,
            pme: 1.2,
            alpha: 0.05
          },
          cashflow_data: [
            { date: '2020-01', contributions: 1000000, distributions: 0, net_cashflow: -1000000 },
            { date: '2020-06', contributions: 500000, distributions: 0, net_cashflow: -500000 },
            { date: '2021-01', contributions: 0, distributions: 200000, net_cashflow: 200000 },
            { date: '2021-06', contributions: 0, distributions: 800000, net_cashflow: 800000 },
            { date: '2022-01', contributions: 0, distributions: 1200000, net_cashflow: 1200000 },
          ],
          nav_data: [
            { date: '2020-01', nav: 1000000, cumulative_nav: 1000000, benchmark_nav: 1000000 },
            { date: '2020-06', nav: 1400000, cumulative_nav: 1400000, benchmark_nav: 1100000 },
            { date: '2021-01', nav: 1200000, cumulative_nav: 1200000, benchmark_nav: 1250000 },
            { date: '2021-06', nav: 800000, cumulative_nav: 800000, benchmark_nav: 1400000 },
            { date: '2022-01', nav: 500000, cumulative_nav: 500000, benchmark_nav: 1600000 },
          ]
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className={`min-h-screen transition-colors duration-200 ${
      darkMode ? 'dark bg-gray-900' : 'bg-gradient-to-br from-blue-50 to-indigo-100'
    }`}>
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-lg border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  PME Calculator
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Private Market Equivalent Analysis
                </p>
              </div>
            </div>
            
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              aria-label="Toggle dark mode"
            >
              {darkMode ? (
                <Sun className="h-5 w-5 text-yellow-500" />
              ) : (
                <Moon className="h-5 w-5 text-gray-600" />
              )}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* File Upload Section */}
        <div className="mb-8">
          <FileDrop onAnalysisComplete={handleAnalysisComplete} />
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                  Analysis Error
                </h3>
                <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                  {error}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results Section */}
        {analysisResults && (
          <>
            {/* KPI Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-8">
              <KpiCard
                title="IRR"
                value={analysisResults.metrics.irr}
                format="percentage"
                icon={<TrendingUp className="h-5 w-5" />}
                trend={analysisResults.metrics.irr > 0 ? 'up' : 'down'}
                description="Internal Rate of Return"
              />
              <KpiCard
                title="TVPI"
                value={analysisResults.metrics.tvpi}
                format="multiple"
                icon={<DollarSign className="h-5 w-5" />}
                trend={analysisResults.metrics.tvpi > 1 ? 'up' : 'down'}
                description="Total Value to Paid-In"
              />
              <KpiCard
                title="DPI"
                value={analysisResults.metrics.dpi}
                format="multiple"
                icon={<BarChart3 className="h-5 w-5" />}
                trend={analysisResults.metrics.dpi > 1 ? 'up' : 'down'}
                description="Distributions to Paid-In"
              />
              <KpiCard
                title="RVPI"
                value={analysisResults.metrics.rvpi}
                format="multiple"
                icon={<TrendingUp className="h-5 w-5" />}
                trend="neutral"
                description="Residual Value to Paid-In"
              />
              <KpiCard
                title="PME"
                value={analysisResults.metrics.pme}
                format="multiple"
                icon={<BarChart3 className="h-5 w-5" />}
                trend={analysisResults.metrics.pme > 1 ? 'up' : 'down'}
                description="Private Market Equivalent"
              />
              <KpiCard
                title="Alpha"
                value={analysisResults.metrics.alpha}
                format="percentage"
                icon={<TrendingUp className="h-5 w-5" />}
                trend={analysisResults.metrics.alpha > 0 ? 'up' : 'down'}
                description="Risk-Adjusted Excess Return"
              />
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
              <CashflowChart 
                data={analysisResults.cashflow_data} 
                loading={loading}
              />
              <NavTimeline 
                data={analysisResults.nav_data} 
                loading={loading}
              />
            </div>
          </>
        )}

        {/* Loading State */}
        {loading && !analysisResults && (
          <div className="text-center py-12">
            <div className="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm shadow rounded-md text-blue-500 bg-blue-100 dark:bg-blue-900 dark:text-blue-200 transition ease-in-out duration-150">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analyzing fund performance...
            </div>
          </div>
        )}

        {/* Welcome Message */}
        {!analysisResults && !loading && (
          <div className="text-center py-12">
            <Upload className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Welcome to PME Calculator
            </h3>
            <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
              Upload your fund cash flows and benchmark data to start analyzing private market equivalent performance.
            </p>
          </div>
        )}
      </main>
    </div>
  );
};

// Extend Window interface for pywebview
declare global {
  interface Window {
    pywebview?: {
      api: {
        run_full_analysis: (fundPath: string, indexPath: string | null) => Promise<{
          success: boolean;
          data?: AnalysisResults;
          error?: string;
        }>;
        fund_metrics: (path: string) => Promise<any>;
        cashflow_data: (path: string) => Promise<any>;
        nav_series: (path: string) => Promise<any>;
      };
    };
  }
}

export default Dashboard;
```

```tsx
// frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import Dashboard from './pages/Dashboard';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Dashboard />
  </React.StrictMode>,
);
```

```css
/* frontend/src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    font-family: 'Inter', system-ui, sans-serif;
  }
  
  body {
    @apply antialiased;
  }
}

@layer components {
  .glassfunds-gradient {
    @apply bg-gradient-to-r from-blue-600 to-indigo-600;
  }
  
  .glassfunds-card {
    @apply bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700;
  }
  
  .glassfunds-button {
    @apply bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .glassfunds-input {
    @apply border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent;
  }
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  @apply bg-gray-100 dark:bg-gray-800;
}

::-webkit-scrollbar-thumb {
  @apply bg-gray-300 dark:bg-gray-600 rounded-full;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400 dark:bg-gray-500;
}
```

## Configuration Files

```json
// frontend/package.json
{
  "name": "pme-calculator-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite --host 0.0.0.0 --port 5173",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "tailwind:build": "tailwindcss -i ./src/index.css -o ./dist/style.css --watch"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "recharts": "^2.8.0",
    "lucide-react": "^0.294.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.2.2",
    "vite": "^5.0.8"
  }
}
```

```javascript
// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        glassfunds: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glassfunds': '0 4px 6px -1px rgba(59, 130, 246, 0.1), 0 2px 4px -1px rgba(59, 130, 246, 0.06)',
      }
    },
  },
  plugins: [],
}
```

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    emptyOutDir: true,
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
  },
})
```

```html
<!-- frontend/index.html -->
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PME Calculator</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

```json
// frontend/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

```json
// frontend/tsconfig.node.json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

```json
// frontend/postcss.config.js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}