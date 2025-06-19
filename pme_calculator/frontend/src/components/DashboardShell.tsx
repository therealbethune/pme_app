import React from 'react'
import { motion } from 'framer-motion'
import { Box } from '@mui/material'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Activity,
  BarChart3,
  PieChart,
  Users,
  Target
} from 'lucide-react'
import { Sidebar } from '../layout/Sidebar'
import { Header } from '../layout/Header'
import { KpiCard } from '../lib/ui/KpiCard'
import { CommandModal } from './CommandModal'

const DashboardShell: React.FC = () => {
  const [commandOpen, setCommandOpen] = React.useState(false)

  // Sample KPI data showcasing the design system
  const kpiData = [
    {
      title: 'Total AUM',
      value: '$2.4B',
      change: { value: '+12.5%', trend: 'up' as const },
      icon: DollarSign
    },
    {
      title: 'Portfolio IRR',
      value: '15.2%',
      change: { value: '+2.1%', trend: 'up' as const },
      icon: TrendingUp
    },
    {
      title: 'Active Funds',
      value: '24',
      change: { value: '+3', trend: 'up' as const },
      icon: PieChart
    },
    {
      title: 'PME Ratio',
      value: '1.18x',
      change: { value: '-0.02x', trend: 'down' as const },
      icon: Activity
    },
    {
      title: 'Net TVPI',
      value: '1.45x',
      change: { value: '+0.08x', trend: 'up' as const },
      icon: BarChart3
    },
    {
      title: 'Vintage Years',
      value: '2019-2024',
      change: { value: '5 years', trend: 'neutral' as const },
      icon: Target
    },
    {
      title: 'LP Count',
      value: '127',
      change: { value: '+8', trend: 'up' as const },
      icon: Users
    },
    {
      title: 'Deployment',
      value: '78%',
      change: { value: '+5%', trend: 'up' as const },
      icon: TrendingUp
    }
  ]

  // Keyboard shortcut handler
  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault()
        setCommandOpen(true)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Header onCommandPaletteOpen={() => setCommandOpen(true)} />
        
        {/* Dashboard Content */}
        <Box component="main" sx={{ flex: 1, p: 3, overflow: 'auto' }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Hero Section */}
            <Box sx={{ mb: 4 }}>
              <motion.h1 
                className="text-3xl font-bold text-gray-900 mb-2"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
              >
                Portfolio Dashboard
              </motion.h1>
              <motion.p 
                className="text-gray-600"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                Scale.ai-grade PME Calculator with professional design system
              </motion.p>
            </Box>

            {/* KPI Grid */}
            <Box 
              sx={{ 
                display: 'grid', 
                gridTemplateColumns: {
                  xs: '1fr',
                  sm: 'repeat(2, 1fr)',
                  md: 'repeat(3, 1fr)',
                  lg: 'repeat(4, 1fr)'
                },
                gap: 3,
                mb: 4
              }}
            >
              {kpiData.map((kpi, index) => (
                <motion.div
                  key={kpi.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                >
                  <KpiCard {...kpi} />
                </motion.div>
              ))}
            </Box>

            {/* Additional Content Sections */}
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' }, gap: 3 }}>
              {/* Main Chart Area */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="bg-white rounded-xl p-6 shadow-sm border border-gray-100"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Analytics</h3>
                <div className="h-64 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">Chart visualization area</p>
                </div>
              </motion.div>

              {/* Side Panel */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
                className="bg-white rounded-xl p-6 shadow-sm border border-gray-100"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
                <div className="space-y-3">
                  {[
                    'Fund Analysis Complete',
                    'New LP Onboarded',
                    'Quarterly Report Generated',
                    'PME Calculation Updated'
                  ].map((activity, index) => (
                    <div key={index} className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span className="text-sm text-gray-700">{activity}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            </Box>
          </motion.div>
        </Box>
      </Box>

      {/* Command Modal */}
      <CommandModal isOpen={commandOpen} onClose={() => setCommandOpen(false)} />
    </Box>
  )
}

export default DashboardShell 