import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, TrendingUp, BarChart3, Calculator } from 'lucide-react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="min-h-full">
      {/* Hero Section with Gradient Background */}
      <section className="relative bg-gradient-to-br from-brand to-blue-600 text-white overflow-hidden">
        <div className="absolute inset-0 grid-bg"></div>
        <div className="relative z-10 px-6 py-20 max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-5xl font-bold mb-6"
            >
              Advanced PME Calculator
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="text-xl mb-8 max-w-2xl mx-auto text-blue-100"
            >
              Analyze private equity performance with institutional-grade 
              Public Market Equivalent calculations and comprehensive risk metrics.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Link
                to="/upload"
                className="inline-flex items-center px-8 py-4 bg-white text-brand font-semibold rounded-xl hover:bg-gray-50 transition-colors shadow-lg"
              >
                Get Started
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
              <Link
                to="/analysis"
                className="inline-flex items-center px-8 py-4 border-2 border-white/30 text-white font-semibold rounded-xl hover:bg-white/10 transition-colors"
              >
                View Demo
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Professional-Grade Analytics
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Built for institutional investors, fund managers, and financial analysts 
            who demand precision and comprehensive reporting.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: Calculator,
              title: 'PME Calculations',
              description: 'Multiple PME methodologies including KS-PME, Direct Alpha, and custom benchmarks',
              color: 'bg-blue-50 text-blue-600'
            },
            {
              icon: BarChart3,
              title: 'Risk Analytics',
              description: 'Volatility analysis, drawdown metrics, and comprehensive risk-adjusted returns',
              color: 'bg-green-50 text-green-600'
            },
            {
              icon: TrendingUp,
              title: 'Performance Insights',
              description: 'Advanced charting, cash flow analysis, and detailed portfolio attribution',
              color: 'bg-purple-50 text-purple-600'
            }
          ].map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 1.0 + index * 0.2 }}
              whileHover={{ 
                y: -4, 
                boxShadow: "0 8px 28px rgba(0,0,0,0.12)" 
              }}
              className="card-hover bg-white p-8 rounded-2xl border border-gray-200 shadow-sm"
            >
              <div className={`w-12 h-12 ${feature.color} rounded-xl flex items-center justify-center mb-6`}>
                <feature.icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Home; 