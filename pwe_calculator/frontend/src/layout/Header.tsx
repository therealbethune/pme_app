import React from 'react';
import { Moon, Sun, Bell, User } from 'lucide-react';
import { motion } from 'framer-motion';

interface HeaderProps {
  isDark?: boolean;
  onToggleDarkMode?: () => void;
}

const Header: React.FC<HeaderProps> = ({ 
  isDark = false, 
  onToggleDarkMode 
}) => {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200 px-4 py-3"
    >
      <div className="flex items-center justify-between">
        {/* Left side - Breadcrumb/Title */}
        <div className="flex items-center space-x-4">
          <h1 className="text-lg font-semibold text-gray-900">
            Fund Performance Analytics
          </h1>
        </div>

        {/* Right side - Actions */}
        <div className="flex items-center space-x-3">
          {/* Notifications */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors relative"
          >
            <Bell className="w-5 h-5 text-gray-600" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
          </motion.button>

          {/* Dark Mode Toggle */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onToggleDarkMode}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            {isDark ? (
              <Sun className="w-5 h-5 text-yellow-500" />
            ) : (
              <Moon className="w-5 h-5 text-gray-600" />
            )}
          </motion.button>

          {/* User Profile */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div className="w-8 h-8 bg-brand rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <span className="text-sm font-medium text-gray-900 hidden sm:block">
              Analyst
            </span>
          </motion.button>
        </div>
      </div>
    </motion.header>
  );
};

export default Header; 