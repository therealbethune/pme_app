import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Settings as SettingsIcon, 
  User, 
  Database, 
  Bell, 
  Shield,
  Save,
  RefreshCw
} from 'lucide-react';

const Settings: React.FC = () => {
  const [settings, setSettings] = useState({
    riskFreeRate: 0.025,
    confidenceLevel: 0.95,
    defaultMethod: 'kaplan_schoar',
    enableNotifications: true,
    autoSave: true,
    cacheEnabled: true
  });

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    // Implementation for saving settings
    console.log('Saving settings:', settings);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="p-6 max-w-4xl mx-auto"
    >
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Settings
        </h1>
        <p className="text-gray-400">
          Configure your PME analysis preferences and system settings
        </p>
      </div>

      <div className="space-y-6">
        {/* Analysis Settings */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="chart-container"
        >
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <SettingsIcon className="w-5 h-5 mr-2 text-primary" />
            Analysis Settings
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Risk-Free Rate
              </label>
              <input
                type="number"
                step="0.001"
                value={settings.riskFreeRate}
                onChange={(e) => handleSettingChange('riskFreeRate', parseFloat(e.target.value))}
                className="input"
                placeholder="0.025"
              />
              <p className="text-xs text-gray-500 mt-1">Default risk-free rate for calculations</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Confidence Level
              </label>
              <select
                value={settings.confidenceLevel}
                onChange={(e) => handleSettingChange('confidenceLevel', parseFloat(e.target.value))}
                className="input"
              >
                <option value={0.90}>90%</option>
                <option value={0.95}>95%</option>
                <option value={0.99}>99%</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">Statistical confidence level</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Default PME Method
              </label>
              <select
                value={settings.defaultMethod}
                onChange={(e) => handleSettingChange('defaultMethod', e.target.value)}
                className="input"
              >
                <option value="kaplan_schoar">Kaplan-Schoar</option>
                <option value="direct_alpha">Direct Alpha</option>
                <option value="pme_plus">PME+</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">Default analysis methodology</p>
            </div>
          </div>
        </motion.div>

        {/* System Settings */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="chart-container"
        >
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <Database className="w-5 h-5 mr-2 text-primary" />
            System Settings
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-white font-medium">Enable Notifications</h4>
                <p className="text-sm text-gray-400">Receive alerts for analysis completion</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.enableNotifications}
                  onChange={(e) => handleSettingChange('enableNotifications', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-white font-medium">Auto-Save Results</h4>
                <p className="text-sm text-gray-400">Automatically save analysis results</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.autoSave}
                  onChange={(e) => handleSettingChange('autoSave', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-white font-medium">Enable Caching</h4>
                <p className="text-sm text-gray-400">Cache analysis results for faster loading</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.cacheEnabled}
                  onChange={(e) => handleSettingChange('cacheEnabled', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>
          </div>
        </motion.div>

        {/* User Profile */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="chart-container"
        >
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <User className="w-5 h-5 mr-2 text-primary" />
            User Profile
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Display Name
              </label>
              <input
                type="text"
                defaultValue="Fund Analyst"
                className="input"
                placeholder="Your display name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Organization
              </label>
              <input
                type="text"
                defaultValue="Internal Team"
                className="input"
                placeholder="Organization name"
              />
            </div>
          </div>
        </motion.div>

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="flex justify-end space-x-4"
        >
          <button className="btn-ghost">
            <RefreshCw className="w-4 h-4 mr-2" />
            Reset to Defaults
          </button>
          <button onClick={handleSave} className="btn-primary">
            <Save className="w-4 h-4 mr-2" />
            Save Settings
          </button>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default Settings; 