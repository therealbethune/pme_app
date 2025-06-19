import React from 'react';
import { motion } from 'framer-motion';
import { BarChart3, Settings, User } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="bg-black border-b border-gray-800 px-6 py-4"
    >
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center space-x-3">
          <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-lg">
            <BarChart3 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">PME Calculator</h1>
            <p className="text-xs text-gray-400">Internal Analysis Tool</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <button className="btn-ghost">
            <Settings className="w-5 h-5" />
          </button>
          <button className="btn-ghost">
            <User className="w-5 h-5" />
          </button>
        </div>
      </div>
    </motion.header>
  );
}; 