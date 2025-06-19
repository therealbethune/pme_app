import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, TrendingUp, BarChart3, Calculator, Shield, Zap, Users } from 'lucide-react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="min-h-full bg-white">
      {/* Hero Section - Scale.com inspired */}
      <section className="relative pt-20 pb-32 bg-gradient-to-br from-primary-50 via-white to-accent overflow-hidden">
        <div className="absolute inset-0 bg-[url('/assets/grid.svg')] opacity-5"></div>
        <div className="relative z-10 px-6 max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center max-w-4xl mx-auto"
          >
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.1 }}
              className="text-hero text-gray-900 mb-8 font-bold tracking-tight"
            >
              Power{' '}
              <span className="bg-gradient-to-r from-primary-600 to-primary-500 bg-clip-text text-transparent">
                Fund Analysis
              </span>
              {' '}With Your Data
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-xl leading-relaxed text-gray-600 mb-12 max-w-3xl mx-auto"
            >
              Make the best investment decisions with the best data. Our PME Calculator powers institutional-grade 
              analysis for private equity funds, leveraging your data to unlock precision insights.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            >
              <Link
                to="/upload"
                className="group inline-flex items-center px-8 py-4 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-all duration-200 shadow-scale hover:shadow-scale-lg transform hover:-translate-y-0.5"
              >
                Start Analysis
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/analysis"
                className="inline-flex items-center px-8 py-4 border-2 border-gray-200 text-gray-700 font-semibold rounded-xl hover:border-primary-300 hover:text-primary-700 transition-all duration-200"
              >
                View Demo
              </Link>
            </motion.div>
          </motion.div>

          {/* Trusted by section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="mt-20 text-center"
          >
            <p className="text-sm font-medium text-gray-500 mb-8">TRUSTED BY LEADING INVESTMENT FIRMS</p>
            <div className="flex items-center justify-center space-x-12 opacity-60">
              <div className="text-2xl font-bold text-gray-400">FIRM A</div>
              <div className="text-2xl font-bold text-gray-400">FIRM B</div>
              <div className="text-2xl font-bold text-gray-400">FIRM C</div>
              <div className="text-2xl font-bold text-gray-400">FIRM D</div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section - Scale.com inspired layout */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="text-center mb-20"
          >
            <h2 className="text-display text-gray-900 mb-6 font-semibold">
              Enterprise-Grade Fund Analysis
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Built for institutional investors who demand precision, scale, and comprehensive reporting 
              across their entire portfolio.
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-3 gap-8">
            {[
              {
                icon: Calculator,
                title: 'Advanced PME Calculations',
                description: 'Multiple PME methodologies including KS-PME, Direct Alpha, and custom benchmarks with institutional-grade precision.',
                color: 'bg-primary-50 text-primary-600'
              },
              {
                icon: Shield,
                title: 'Risk Analytics Suite',
                description: 'Comprehensive volatility analysis, drawdown metrics, and risk-adjusted returns with stress testing capabilities.',
                color: 'bg-green-50 text-green-600'
              },
              {
                icon: Zap,
                title: 'Real-time Insights',
                description: 'Advanced charting, cash flow analysis, and detailed portfolio attribution with automated reporting.',
                color: 'bg-purple-50 text-purple-600'
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.8 + index * 0.1 }}
                className="group bg-white p-8 rounded-2xl shadow-scale hover:shadow-scale-lg transition-all duration-300 hover:-translate-y-1"
              >
                <div className={`w-14 h-14 ${feature.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-7 h-7" />
                </div>
                <h3 className="text-title text-gray-900 mb-4 font-semibold">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section - Scale.com inspired */}
      <section className="py-24 px-6 bg-gradient-to-r from-primary-600 to-primary-700">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.0 }}
          >
            <h2 className="text-display text-white mb-6 font-semibold">
              Ready to Transform Your Fund Analysis?
            </h2>
            <p className="text-xl text-primary-100 mb-10 leading-relaxed">
              Join leading institutional investors who trust our platform for mission-critical investment decisions.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/upload"
                className="inline-flex items-center px-8 py-4 bg-white text-primary-700 font-semibold rounded-xl hover:bg-gray-50 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Get Started Today
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
              <Link
                to="/analysis"
                className="inline-flex items-center px-8 py-4 border-2 border-primary-400 text-white font-semibold rounded-xl hover:bg-primary-500 transition-all duration-200"
              >
                Schedule Demo
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Home; 