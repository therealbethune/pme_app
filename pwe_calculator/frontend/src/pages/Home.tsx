import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  BarChart3, 
  Upload, 
  TrendingUp, 
  Database,
  ArrowRight,
  Activity,
  DollarSign,
  Target
} from 'lucide-react';

const Home: React.FC = () => {
  const quickActions = [
    {
      title: 'Upload Data',
      description: 'Upload fund and benchmark data for analysis',
      icon: Upload,
      href: '/upload',
      color: 'bg-blue-900/20 border-blue-800 hover:border-blue-700',
      iconColor: 'text-blue-400'
    },
    {
      title: 'View Analysis',
      description: 'Review existing PME analysis results',
      icon: BarChart3,
      href: '/analysis',
      color: 'bg-green-900/20 border-green-800 hover:border-green-700',
      iconColor: 'text-green-400'
    },
    {
      title: 'Portfolio Overview',
      description: 'Manage your fund portfolio',
      icon: Database,
      href: '/portfolio',
      color: 'bg-purple-900/20 border-purple-800 hover:border-purple-700',
      iconColor: 'text-purple-400'
    }
  ];

  const recentMetrics = [
    {
      label: 'Latest Analysis',
      value: '18.5% IRR',
      change: '+2.3%',
      icon: TrendingUp,
      positive: true
    },
    {
      label: 'Portfolio Value',
      value: '$125M',
      change: '+8.7%',
      icon: DollarSign,
      positive: true
    },
    {
      label: 'Active Funds',
      value: '3',
      change: 'No change',
      icon: Target,
      positive: null
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="p-6 max-w-7xl mx-auto"
    >
      {/* Welcome Section */}
      <div className="mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <h1 className="text-4xl font-bold text-white mb-3">
            PME Analysis Dashboard
          </h1>
          <p className="text-xl text-gray-400 mb-6">
            Welcome to your private equity performance analysis platform
          </p>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-white mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {quickActions.map((action, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 + index * 0.1 }}
            >
              <Link
                to={action.href}
                className={`block p-6 rounded-xl border transition-all duration-200 hover:-translate-y-1 ${action.color}`}
              >
                <div className="flex items-center justify-between mb-4">
                  <action.icon className={`w-8 h-8 ${action.iconColor}`} />
                  <ArrowRight className="w-5 h-5 text-gray-500" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  {action.title}
                </h3>
                <p className="text-gray-400 text-sm">
                  {action.description}
                </p>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Recent Metrics */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-white mb-6">Recent Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {recentMetrics.map((metric, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 + index * 0.1 }}
              className="metric-card"
            >
              <div className="flex items-center justify-between mb-4">
                <metric.icon className="w-6 h-6 text-primary" />
                {metric.positive !== null && (
                  <span className={`text-xs font-medium ${
                    metric.positive ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {metric.change}
                  </span>
                )}
              </div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">
                {metric.label}
              </h3>
              <p className="text-2xl font-bold text-white">
                {metric.value}
              </p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* System Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.7 }}
        className="chart-container"
      >
        <h2 className="text-2xl font-semibold text-white mb-6">System Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-900/50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-medium">Analysis Engine</h3>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm text-green-400">Online</span>
              </div>
            </div>
            <p className="text-gray-400 text-sm">
              All analysis services are operational
            </p>
          </div>

          <div className="bg-gray-900/50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-medium">Data Processing</h3>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm text-green-400">Ready</span>
              </div>
            </div>
            <p className="text-gray-400 text-sm">
              Ready to process new uploads
            </p>
          </div>

          <div className="bg-gray-900/50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-medium">Cache System</h3>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm text-green-400">Active</span>
              </div>
            </div>
            <p className="text-gray-400 text-sm">
              Results cached for fast retrieval
            </p>
          </div>

          <div className="bg-gray-900/50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-medium">API Status</h3>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm text-green-400">Healthy</span>
              </div>
            </div>
            <p className="text-gray-400 text-sm">
              All endpoints responding normally
            </p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default Home; 