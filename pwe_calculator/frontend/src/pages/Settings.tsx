import React from 'react';
import { motion } from 'framer-motion';
import { Settings as SettingsIcon, User, Bell, Shield } from 'lucide-react';

const Settings: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="p-6 max-w-4xl mx-auto"
    >
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Settings
        </h1>
        <p className="text-gray-600">
          Configure your application preferences and account settings
        </p>
      </div>

      <div className="space-y-6">
        {[
          {
            title: 'Profile Settings',
            icon: User,
            description: 'Manage your personal information and preferences',
            items: ['Name', 'Email', 'Role', 'Organization']
          },
          {
            title: 'Notifications',
            icon: Bell,
            description: 'Configure how you receive updates and alerts',
            items: ['Email notifications', 'Analysis alerts', 'Report delivery']
          },
          {
            title: 'Security',
            icon: Shield,
            description: 'Manage your account security and access',
            items: ['Password', 'Two-factor auth', 'API keys', 'Session management']
          },
          {
            title: 'Calculation Settings',
            icon: SettingsIcon,
            description: 'Configure default analysis parameters',
            items: ['Benchmark selection', 'Risk-free rate', 'Calculation methods']
          }
        ].map((section, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm"
          >
            <div className="flex items-start space-x-4">
              <div className="w-10 h-10 bg-brand/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <section.icon className="w-5 h-5 text-brand" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {section.title}
                </h3>
                <p className="text-gray-600 mb-4">
                  {section.description}
                </p>
                <div className="space-y-2">
                  {section.items.map((item, itemIndex) => (
                    <div key={itemIndex} className="flex justify-between items-center py-2">
                      <span className="text-sm text-gray-700">{item}</span>
                      <button className="text-sm text-brand hover:text-brand/80 font-medium">
                        Configure
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default Settings; 