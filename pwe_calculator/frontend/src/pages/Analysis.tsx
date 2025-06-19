import React from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, PieChart } from 'lucide-react';

const Analysis: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="p-6 max-w-7xl mx-auto"
    >
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          PME Analysis
        </h1>
        <p className="text-gray-600">
          Comprehensive performance analysis and benchmarking
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          {
            title: 'PME Metrics',
            icon: BarChart3,
            value: '1.23x',
            change: '+12.3%',
            color: 'text-green-600'
          },
          {
            title: 'Direct Alpha',
            icon: TrendingUp,
            value: '4.2%',
            change: '+0.8%',
            color: 'text-blue-600'
          },
          {
            title: 'Risk Metrics',
            icon: PieChart,
            value: '18.5%',
            change: '-2.1%',
            color: 'text-purple-600'
          }
        ].map((metric, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            whileHover={{ y: -4, boxShadow: "0 8px 28px rgba(0,0,0,0.12)" }}
            className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm"
          >
            <div className="flex items-center justify-between mb-4">
              <metric.icon className={`w-8 h-8 ${metric.color}`} />
              <span className={`text-sm font-medium ${metric.color}`}>
                {metric.change}
              </span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {metric.title}
            </h3>
            <p className="text-2xl font-bold text-gray-900">
              {metric.value}
            </p>
          </motion.div>
        ))}
      </div>

      <div className="mt-8 bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Performance Chart
        </h3>
        <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
          <p className="text-gray-500">Chart visualization will appear here</p>
        </div>
      </div>
    </motion.div>
  );
};

export default Analysis; 