import React from 'react';
import { motion } from 'framer-motion';
import { Briefcase, DollarSign, Calendar } from 'lucide-react';

const Portfolio: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="p-6 max-w-7xl mx-auto"
    >
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Portfolio Overview
        </h1>
        <p className="text-gray-600">
          Manage and track your private equity investments
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        {[
          {
            title: 'Total AUM',
            icon: DollarSign,
            value: '$2.4B',
            subtext: 'Across 12 funds'
          },
          {
            title: 'Active Investments',
            icon: Briefcase,
            value: '34',
            subtext: 'Portfolio companies'
          },
          {
            title: 'Avg. Holding Period',
            icon: Calendar,
            value: '4.2 years',
            subtext: 'Median exit timeline'
          }
        ].map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm"
          >
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-brand/10 rounded-lg flex items-center justify-center mr-3">
                <stat.icon className="w-5 h-5 text-brand" />
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-600">{stat.title}</h3>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
            <p className="text-sm text-gray-500">{stat.subtext}</p>
          </motion.div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Fund Performance
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-900">Fund</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Vintage</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">PME</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">IRR</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Multiple</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: 'Growth Fund I', vintage: '2018', pme: '1.23x', irr: '15.2%', multiple: '1.4x' },
                { name: 'Value Fund II', vintage: '2019', pme: '1.18x', irr: '12.8%', multiple: '1.3x' },
                { name: 'Balanced Fund', vintage: '2020', pme: '1.15x', irr: '11.5%', multiple: '1.2x' }
              ].map((fund, index) => (
                <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 font-medium text-gray-900">{fund.name}</td>
                  <td className="py-3 px-4 text-gray-600">{fund.vintage}</td>
                  <td className="py-3 px-4 text-green-600 font-medium">{fund.pme}</td>
                  <td className="py-3 px-4 text-gray-900">{fund.irr}</td>
                  <td className="py-3 px-4 text-gray-900">{fund.multiple}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
};

export default Portfolio; 