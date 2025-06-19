import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  DollarSign, 
  BarChart3, 
  PieChart,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react'
import { Sidebar } from '../layout/Sidebar'
import { Header } from '../layout/Header'
import { CommandModal } from './CommandModal'
import { KpiCard } from '../lib/ui/KpiCard'

export function DashboardShell() {
  const [isCommandModalOpen, setIsCommandModalOpen] = useState(false)

  // Global keyboard shortcut for command palette
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setIsCommandModalOpen(true)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <div className="min-h-screen bg-surface">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Header */}
      <Header onCommandPaletteOpen={() => setIsCommandModalOpen(true)} />
      
      {/* Main content */}
      <main className="ml-64 pt-20 p-6">
        {/* Page header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-base-900 mb-2">
            PME Dashboard
          </h1>
          <p className="text-base-600">
            Private Market Equivalent analysis with 4x faster performance
          </p>
        </motion.div>

        {/* KPI Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <KpiCard
            title="Total PME Ratio"
            value="1.18"
            change={{ value: '+12.5%', trend: 'up' }}
            icon={TrendingUp}
            delay={0}
          />
          <KpiCard
            title="Fund IRR"
            value="15.2%"
            change={{ value: '+2.3%', trend: 'up' }}
            icon={ArrowUpRight}
            delay={0.1}
          />
          <KpiCard
            title="Total Value"
            value="$2.4M"
            change={{ value: '+8.7%', trend: 'up' }}
            icon={DollarSign}
            delay={0.2}
          />
          <KpiCard
            title="Active Funds"
            value="12"
            change={{ value: '2 new', trend: 'neutral' }}
            icon={PieChart}
            delay={0.3}
          />
        </div>

        {/* Charts Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
        >
          {/* Performance Chart */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 border-l-4 border-l-brand">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-base-900">
                Performance Overview
              </h3>
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="p-2 bg-brand/10 rounded-lg"
              >
                <BarChart3 className="w-5 h-5 text-brand" />
              </motion.div>
            </div>
            <div className="h-64 bg-gradient-to-br from-brand/5 to-transparent rounded-xl flex items-center justify-center">
              <p className="text-base-500">Chart placeholder - Connect to your existing charts</p>
            </div>
          </div>

          {/* Portfolio Allocation */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 border-l-4 border-l-brand">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-base-900">
                Portfolio Allocation
              </h3>
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="p-2 bg-brand/10 rounded-lg"
              >
                <PieChart className="w-5 h-5 text-brand" />
              </motion.div>
            </div>
            <div className="h-64 bg-gradient-to-br from-brand/5 to-transparent rounded-xl flex items-center justify-center">
              <p className="text-base-500">Chart placeholder - Connect to your existing charts</p>
            </div>
          </div>
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 border-l-4 border-l-brand"
        >
          <h3 className="text-lg font-semibold text-base-900 mb-6">
            Recent Activity
          </h3>
          <div className="space-y-4">
            {[
              { action: 'Fund data uploaded', file: 'fund_style_index.csv', time: '2 hours ago' },
              { action: 'Analysis completed', result: 'PME ratio: 1.18', time: '2 hours ago' },
              { action: 'Report generated', file: 'Portfolio_Report.pdf', time: '1 day ago' },
            ].map((activity, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.6 + index * 0.1 }}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
              >
                <div>
                  <p className="font-medium text-base-900">{activity.action}</p>
                  <p className="text-sm text-base-600">
                    {activity.file || activity.result}
                  </p>
                </div>
                <span className="text-sm text-base-500">{activity.time}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </main>

      {/* Command Modal */}
      <CommandModal
        isOpen={isCommandModalOpen}
        onClose={() => setIsCommandModalOpen(false)}
      />
    </div>
  )
} 