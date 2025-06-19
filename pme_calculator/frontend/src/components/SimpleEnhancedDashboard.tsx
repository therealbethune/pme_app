import React from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  DollarSign, 
  Activity,
  BarChart3,
  PieChart,
  Users,
  Target,
  ArrowUp,
  Download,
  Upload,
  HelpCircle,
  ChevronRight,
  Award
} from 'lucide-react'
import { GlassStatCard } from './ui/GlassStatCard'

const SimpleEnhancedDashboard: React.FC = () => {
  const handleScrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleExport = () => {
    console.log('Export CSV clicked')
  }

  const handleUpload = () => {
    console.log('Upload Data clicked')
  }

  const handleHelp = () => {
    console.log('Help clicked')
  }

  const kpiData = [
    {
      label: 'Total AUM',
      value: 2400,
      suffix: 'M',
      prefix: '$',
      icon: DollarSign,
      delta: { value: 12.5, isPositive: true }
    },
    {
      label: 'Portfolio IRR',
      value: 15.2,
      suffix: '%',
      icon: TrendingUp,
      delta: { value: 2.1, isPositive: true }
    },
    {
      label: 'Active Funds',
      value: 24,
      icon: PieChart,
      delta: { value: 3, isPositive: true }
    },
    {
      label: 'PME Ratio',
      value: 1.18,
      suffix: 'x',
      icon: Activity,
      delta: { value: -0.02, isPositive: false }
    },
    {
      label: 'Net TVPI',
      value: 1.45,
      suffix: 'x',
      icon: BarChart3,
      delta: { value: 0.08, isPositive: true }
    },
    {
      label: 'LP Count',
      value: 127,
      icon: Users,
      delta: { value: 8, isPositive: true }
    }
  ]

  const features = [
    {
      icon: BarChart3,
      title: 'Advanced Analytics',
      description: 'Professional-grade PME calculations with real-time performance metrics and comprehensive reporting.',
      highlight: 'Real-time insights'
    },
    {
      icon: TrendingUp,
      title: 'Performance Tracking',
      description: 'Monitor fund performance across multiple vintages with detailed IRR and TVPI analysis.',
      highlight: 'Multi-vintage analysis'
    },
    {
      icon: Target,
      title: 'Benchmarking',
      description: 'Compare portfolio performance against industry benchmarks and peer groups.',
      highlight: 'Industry comparison'
    },
    {
      icon: Users,
      title: 'LP Management',
      description: 'Comprehensive limited partner management with detailed reporting and communication tools.',
      highlight: 'Full LP suite'
    }
  ]

  const recentActivities = [
    { label: 'Q4 Performance Report Generated', time: '2 min ago', type: 'success' },
    { label: 'New Fund Added: Tech Growth III', time: '1 hour ago', type: 'info' },
    { label: 'LP Quarterly Update Sent', time: '3 hours ago', type: 'default' },
    { label: 'Benchmark Data Updated', time: '1 day ago', type: 'warning' }
  ]

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      {/* Noise texture overlay */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-5 z-0"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'repeat',
          backgroundSize: '256px 256px',
        }}
      />

      <div className="relative z-10">
        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
          {/* Radial gradient background */}
          <div className="absolute inset-0 opacity-30">
            <div 
              className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[75vw] h-[75vh] blur-3xl bg-cyan-500/10 rounded-full"
            />
          </div>

          {/* Glass content container */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="relative max-w-4xl mx-auto bg-black/30 backdrop-blur-lg ring-1 ring-cyan-400/20 rounded-3xl p-16 space-y-8 text-center"
          >
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6 }}
              className="text-6xl font-bold text-gray-100 tracking-tight leading-none"
            >
              Professional{' '}
              <span className="bg-gradient-to-r from-cyan-400 to-cyan-600 bg-clip-text text-transparent">
                PME Calculator
              </span>
            </motion.h1>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.6 }}
              className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed"
            >
              Advanced private equity performance measurement with institutional-grade analytics, 
              comprehensive reporting, and real-time benchmarking capabilities.
            </motion.p>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.6 }}
              className="pt-8"
            >
              <button className="bg-cyan-400 hover:bg-cyan-500 text-black font-semibold px-12 py-4 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
                Get Started
              </button>
            </motion.div>
          </motion.div>
        </section>

        {/* KPI Section */}
        <section className="py-24 px-8">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="text-center mb-20"
            >
              <h2 className="text-5xl font-bold mb-8 bg-gradient-to-r from-gray-100 to-cyan-400 bg-clip-text text-transparent">
                Portfolio Performance
              </h2>
              <p className="text-gray-300 text-xl max-w-2xl mx-auto">
                Real-time insights into your private equity portfolio performance
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 justify-items-center">
              {kpiData.map((kpi, index) => (
                <motion.div
                  key={kpi.label}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1, duration: 0.6 }}
                  viewport={{ once: true }}
                >
                  <GlassStatCard {...kpi} />
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Main Content Grid */}
        <section className="py-24 px-8">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Chart Area */}
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6 }}
                viewport={{ once: true }}
                className="lg:col-span-2"
              >
                <div className="bg-black/30 backdrop-blur-sm ring-1 ring-cyan-400/20 rounded-3xl p-8 h-96">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="p-2 bg-cyan-400/10 rounded-xl">
                      <BarChart3 size={24} className="text-cyan-400" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-100">
                      Performance Analytics
                    </h3>
                  </div>
                  
                  <div className="h-64 border-2 border-dashed border-cyan-400/30 rounded-2xl flex items-center justify-center">
                    <div className="text-center">
                      <Award size={48} className="text-cyan-400 mx-auto mb-4" />
                      <p className="text-gray-300 text-lg">
                        Interactive Chart Visualization
                      </p>
                      <p className="text-gray-400 text-sm mt-2">
                        Real-time performance metrics and trends
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Recent Activity */}
              <motion.div
                initial={{ opacity: 0, x: 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6 }}
                viewport={{ once: true }}
              >
                <div className="bg-black/30 backdrop-blur-sm ring-1 ring-cyan-400/20 rounded-3xl p-8 h-96">
                  <h3 className="text-xl font-bold text-gray-100 mb-6">
                    Recent Activity
                  </h3>
                  
                  <div className="space-y-4">
                    {recentActivities.map((activity, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: 20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1, duration: 0.4 }}
                        viewport={{ once: true }}
                        className="relative bg-gray-800/50 rounded-2xl px-4 py-3 text-gray-300 hover:bg-gray-700/50 transition-colors duration-200"
                      >
                        {/* Neon accent bar */}
                        <div className="absolute left-0 top-0 h-full w-1 rounded-l-2xl bg-cyan-400 opacity-70" />
                        
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-100">
                            {activity.label}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {activity.time}
                          </p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section className="py-24 px-8 bg-gradient-to-b from-transparent to-gray-800/20">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="text-center mb-20"
            >
              <h2 className="text-5xl font-bold mb-8 text-gray-100">
                Enterprise-Grade Features
              </h2>
              <p className="text-gray-300 text-xl max-w-2xl mx-auto">
                Built for institutional investors with the precision and reliability you demand
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1, duration: 0.6 }}
                  viewport={{ once: true }}
                  className="bg-black/30 backdrop-blur-sm ring-1 ring-cyan-400/20 rounded-3xl p-8 hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 group cursor-pointer"
                >
                  <div className="flex items-start space-x-6">
                    <div className="p-3 bg-cyan-400/10 rounded-2xl group-hover:bg-cyan-400/20 transition-colors duration-300">
                      <feature.icon size={28} className="text-cyan-400" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="text-xl font-bold text-gray-100">
                          {feature.title}
                        </h3>
                        <span className="text-xs bg-cyan-400/20 text-cyan-400 px-2 py-1 rounded-full font-medium">
                          {feature.highlight}
                        </span>
                      </div>
                      <p className="text-gray-300 leading-relaxed mb-4">
                        {feature.description}
                      </p>
                      <div className="flex items-center text-cyan-400 text-sm font-medium group-hover:gap-2 transition-all duration-300">
                        Learn more
                        <ChevronRight size={16} className="ml-1 group-hover:translate-x-1 transition-transform duration-300" />
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Floating Quick Actions */}
        <div className="fixed bottom-8 right-8 z-50 flex flex-col gap-4">
          <button 
            onClick={handleUpload}
            className="relative h-12 w-12 rounded-full bg-cyan-400 text-black shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 flex items-center justify-center"
            title="Upload Data"
          >
            <Upload size={18} />
          </button>
          <button 
            onClick={handleExport}
            className="relative h-12 w-12 rounded-full bg-cyan-400 text-black shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 flex items-center justify-center"
            title="Export CSV"
          >
            <Download size={18} />
          </button>
          <button 
            onClick={handleHelp}
            className="relative h-12 w-12 rounded-full bg-cyan-400 text-black shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 flex items-center justify-center"
            title="Help"
          >
            <HelpCircle size={18} />
          </button>
          <button 
            onClick={handleScrollToTop}
            className="relative h-14 w-14 rounded-full bg-cyan-400 text-black shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 flex items-center justify-center"
            title="Scroll to Top"
          >
            <ArrowUp size={20} />
          </button>
        </div>

        {/* Footer */}
        <footer className="relative bg-gray-900 text-gray-300 py-20 border-t border-cyan-400/20">
          {/* Animated aurora strip */}
          <div className="absolute top-0 inset-x-0 h-1 bg-cyan-400 opacity-60 animate-pulse" />
          
          <div className="max-w-7xl mx-auto px-8 text-center">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="mb-8 md:mb-0">
                <p className="text-gray-300">
                  © 2024 PME Calculator. Professional-grade portfolio analytics.
                </p>
              </div>
              <div className="flex space-x-8">
                <a href="#" className="text-gray-300 hover:text-cyan-400 transition-colors duration-300">
                  Privacy
                </a>
                <a href="#" className="text-gray-300 hover:text-cyan-400 transition-colors duration-300">
                  Terms
                </a>
                <a href="#" className="text-gray-300 hover:text-cyan-400 transition-colors duration-300">
                  Support
                </a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default SimpleEnhancedDashboard 