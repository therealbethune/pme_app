import React from 'react';
import { motion } from 'framer-motion';
import { 
  Briefcase, 
  TrendingUp, 
  DollarSign, 
  Calendar,
  Plus,
  Filter
} from 'lucide-react';

const Portfolio: React.FC = () => {
  const portfolios = [
    {
      id: 1,
      name: 'Growth Fund I',
      vintage: 2020,
      commitment: 50000000,
      deployed: 35000000,
      nav: 42000000,
      irr: 0.18,
      status: 'Active'
    },
    {
      id: 2,
      name: 'Value Fund II',
      vintage: 2019,
      commitment: 75000000,
      deployed: 68000000,
      nav: 85000000,
      irr: 0.22,
      status: 'Active'
    },
    {
      id: 3,
      name: 'Buyout Fund III',
      vintage: 2018,
      commitment: 100000000,
      deployed: 95000000,
      nav: 125000000,
      irr: 0.16,
      status: 'Mature'
    }
  ];

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value: number): string => {
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="p-6 max-w-7xl mx-auto"
    >
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            Portfolio Management
          </h1>
          <p className="text-gray-400">
            Manage and analyze your private equity portfolio
          </p>
        </div>
        <div className="flex gap-3">
          <button className="btn-ghost">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </button>
          <button className="btn-primary">
            <Plus className="w-4 h-4 mr-2" />
            Add Fund
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="metric-card bg-blue-900/20 border-blue-800"
        >
          <div className="flex items-center justify-between mb-4">
            <Briefcase className="w-8 h-8 text-blue-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-1">Total Funds</h3>
          <p className="text-2xl font-bold text-white">3</p>
          <p className="text-xs text-gray-400">Active portfolios</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="metric-card bg-green-900/20 border-green-800"
        >
          <div className="flex items-center justify-between mb-4">
            <DollarSign className="w-8 h-8 text-green-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-1">Total Commitment</h3>
          <p className="text-2xl font-bold text-white">{formatCurrency(225000000)}</p>
          <p className="text-xs text-gray-400">Across all funds</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="metric-card bg-purple-900/20 border-purple-800"
        >
          <div className="flex items-center justify-between mb-4">
            <TrendingUp className="w-8 h-8 text-purple-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-1">Portfolio IRR</h3>
          <p className="text-2xl font-bold text-white">{formatPercentage(0.185)}</p>
          <p className="text-xs text-gray-400">Weighted average</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="metric-card bg-orange-900/20 border-orange-800"
        >
          <div className="flex items-center justify-between mb-4">
            <Calendar className="w-8 h-8 text-orange-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-1">Avg Vintage</h3>
          <p className="text-2xl font-bold text-white">2019</p>
          <p className="text-xs text-gray-400">Portfolio vintage</p>
        </motion.div>
      </div>

      {/* Portfolio Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
        className="chart-container"
      >
        <h3 className="text-lg font-semibold text-white mb-4">Fund Portfolio</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800">
                <th className="text-left py-3 px-4 text-gray-300 font-medium">Fund Name</th>
                <th className="text-left py-3 px-4 text-gray-300 font-medium">Vintage</th>
                <th className="text-right py-3 px-4 text-gray-300 font-medium">Commitment</th>
                <th className="text-right py-3 px-4 text-gray-300 font-medium">Deployed</th>
                <th className="text-right py-3 px-4 text-gray-300 font-medium">NAV</th>
                <th className="text-right py-3 px-4 text-gray-300 font-medium">IRR</th>
                <th className="text-center py-3 px-4 text-gray-300 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {portfolios.map((portfolio, index) => (
                <motion.tr
                  key={portfolio.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: 0.6 + index * 0.1 }}
                  className="border-b border-gray-800/50 hover:bg-gray-900/30 transition-colors"
                >
                  <td className="py-4 px-4">
                    <div className="font-medium text-white">{portfolio.name}</div>
                  </td>
                  <td className="py-4 px-4 text-gray-300">{portfolio.vintage}</td>
                  <td className="py-4 px-4 text-right text-white">
                    {formatCurrency(portfolio.commitment)}
                  </td>
                  <td className="py-4 px-4 text-right text-white">
                    {formatCurrency(portfolio.deployed)}
                  </td>
                  <td className="py-4 px-4 text-right text-white">
                    {formatCurrency(portfolio.nav)}
                  </td>
                  <td className="py-4 px-4 text-right text-green-400 font-medium">
                    {formatPercentage(portfolio.irr)}
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span className={`status-indicator ${
                      portfolio.status === 'Active' 
                        ? 'status-success' 
                        : 'status-info'
                    }`}>
                      {portfolio.status}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default Portfolio; 