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
  Sparkles,
  ChevronRight
} from 'lucide-react'
import { HeroHeader } from './ui/HeroHeader'
import { NeonCard } from './ui/NeonCard'
import { StatTile } from './ui/StatTile'
import { ButtonGlow } from './ui/ButtonGlow'

const NeonDashboard: React.FC = () => {
  const handleGetStarted = () => {
    // Navigate to upload or analysis page
    console.log('Get started clicked')
  }

  const handleScrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const kpiData = [
    {
      label: 'Total AUM',
      valueFrom: 0,
      valueTo: 2400,
      suffix: 'M',
      prefix: '$',
      icon: DollarSign
    },
    {
      label: 'Portfolio IRR',
      valueFrom: 0,
      valueTo: 15.2,
      suffix: '%',
      icon: TrendingUp
    },
    {
      label: 'Active Funds',
      valueFrom: 0,
      valueTo: 24,
      icon: PieChart
    },
    {
      label: 'PME Ratio',
      valueFrom: 0,
      valueTo: 1.18,
      suffix: 'x',
      icon: Activity
    },
    {
      label: 'Net TVPI',
      valueFrom: 0,
      valueTo: 1.45,
      suffix: 'x',
      icon: BarChart3
    },
    {
      label: 'LP Count',
      valueFrom: 0,
      valueTo: 127,
      icon: Users
    }
  ]

  const features = [
    {
      icon: BarChart3,
      title: 'Advanced Analytics',
      description: 'Professional-grade PME calculations with real-time performance metrics and comprehensive reporting.'
    },
    {
      icon: TrendingUp,
      title: 'Performance Tracking',
      description: 'Monitor fund performance across multiple vintages with detailed IRR and TVPI analysis.'
    },
    {
      icon: Target,
      title: 'Benchmarking',
      description: 'Compare portfolio performance against industry benchmarks and peer groups.'
    },
    {
      icon: Users,
      title: 'LP Management',
      description: 'Comprehensive limited partner management with detailed reporting and communication tools.'
    }
  ]

  return (
    <div className="min-h-screen bg-bg-base text-text-primary">
      {/* Hero Section */}
      <HeroHeader
        title="Professional PME Calculator"
        subtitle="Advanced private equity performance measurement with institutional-grade analytics, comprehensive reporting, and real-time benchmarking capabilities."
        ctaText="Get Started"
        onCtaClick={handleGetStarted}
      />

      {/* Main Content */}
      <div className="relative">
        {/* KPI Section */}
        <section className="py-20 px-4">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-4xl font-bold mb-6 bg-gradient-to-r from-text-primary to-accent bg-clip-text text-transparent">
                Portfolio Performance
              </h2>
              <p className="text-text-muted text-lg max-w-2xl mx-auto">
                Real-time insights into your private equity portfolio performance
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {kpiData.map((kpi, index) => (
                <motion.div
                  key={kpi.label}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1, duration: 0.6 }}
                  viewport={{ once: true }}
                >
                  <StatTile {...kpi} />
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 px-4 bg-gradient-to-b from-transparent to-bg-elevated/20">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-4xl font-bold mb-6">
                Enterprise-Grade Features
              </h2>
              <p className="text-text-muted text-lg max-w-2xl mx-auto">
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
                >
                  <NeonCard>
                    <div className="flex items-start space-x-4">
                      <div className="p-3 bg-accent/10 rounded-xl">
                        <feature.icon size={24} className="text-accent" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-xl font-semibold text-text-primary mb-2">
                          {feature.title}
                        </h3>
                        <p className="text-text-muted leading-relaxed">
                          {feature.description}
                        </p>
                        <div className="mt-4 flex items-center text-accent text-sm font-medium">
                          Learn more
                          <ChevronRight size={16} className="ml-1" />
                        </div>
                      </div>
                    </div>
                  </NeonCard>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl font-bold mb-6">
                Ready to Transform Your Portfolio Analysis?
              </h2>
              <p className="text-text-muted text-lg mb-8 max-w-2xl mx-auto">
                Join leading institutional investors who trust our platform for accurate, 
                real-time private equity performance measurement.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <button
                  onClick={handleGetStarted}
                  className="bg-accent hover:bg-accent/80 text-bg-base font-medium px-8 py-4 rounded-xl shadow-neon hover:shadow-neon-lg transition-all duration-300 transform hover:scale-105"
                >
                  Start Analysis
                </button>
                <button className="text-text-muted hover:text-accent transition-colors duration-300 flex items-center">
                  View Documentation
                  <ChevronRight size={16} className="ml-1" />
                </button>
              </div>
            </motion.div>
          </div>
        </section>
      </div>

      {/* Floating Action Button */}
      <div className="fixed bottom-8 right-8 z-50">
        <ButtonGlow onClick={handleScrollToTop}>
          <ArrowUp size={20} />
        </ButtonGlow>
      </div>

      {/* Aurora Footer Strip */}
      <footer className="relative bg-bg-base text-text-muted py-16 border-t border-white/5">
        {/* Animated aurora strip */}
        <div className="absolute top-0 inset-x-0 h-1.5 bg-accent opacity-80 animate-pulse-slow" 
             style={{
               maskImage: 'linear-gradient(90deg, transparent, white, transparent)'
             }}
        />
        
        <div className="max-w-7xl mx-auto px-4 text-center">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <p className="text-sm">
                © 2024 PME Calculator. Professional-grade portfolio analytics.
              </p>
            </div>
            <div className="flex space-x-6">
              <a href="#" className="text-sm hover:text-accent transition-colors">
                Privacy
              </a>
              <a href="#" className="text-sm hover:text-accent transition-colors">
                Terms
              </a>
              <a href="#" className="text-sm hover:text-accent transition-colors">
                Support
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default NeonDashboard 