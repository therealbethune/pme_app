import React from 'react';
import { motion } from 'framer-motion';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  Upload, 
  BarChart3, 
  FileText, 
  Settings,
  Database,
  TrendingUp
} from 'lucide-react';

const navigationItems = [
  {
    name: 'Home',
    href: '/',
    icon: Home,
  },
  {
    name: 'Data Upload',
    href: '/upload',
    icon: Upload,
  },
  {
    name: 'Analysis',
    href: '/analysis',
    icon: BarChart3,
  },
  {
    name: 'Portfolio',
    href: '/portfolio',
    icon: Database,
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: FileText,
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
  },
];

export const Sidebar: React.FC = () => {
  return (
    <motion.aside
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6 }}
      className="w-64 bg-gray-950 border-r border-gray-800 min-h-screen"
    >
      <div className="p-6">
        <div className="flex items-center space-x-3 mb-8">
          <div className="flex items-center justify-center w-8 h-8 bg-primary rounded-lg">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">PME Analysis</h2>
            <p className="text-xs text-gray-400">Internal Tool</p>
          </div>
        </div>

        <nav className="space-y-2">
          {navigationItems.map((item, index) => (
            <motion.div
              key={item.name}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
            >
              <NavLink
                to={item.href}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-primary text-white shadow-lg'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  }`
                }
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.name}</span>
              </NavLink>
            </motion.div>
          ))}
        </nav>
      </div>

      <div className="absolute bottom-6 left-6 right-6">
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <h3 className="text-white font-medium mb-2">Analysis Status</h3>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span className="text-sm text-gray-400">System Ready</span>
          </div>
        </div>
      </div>
    </motion.aside>
  );
}; 