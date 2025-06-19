import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Search, 
  Bell, 
  User, 
  Settings,
  LogOut,
  Command
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface HeaderProps {
  className?: string
  onCommandPaletteOpen?: () => void
}

export function Header({ className, onCommandPaletteOpen }: HeaderProps) {
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)

  return (
    <header className={cn(
      'fixed top-0 right-0 left-64 z-30 bg-white/80 backdrop-blur-sm border-b border-gray-200',
      className
    )}>
      <div className="flex items-center justify-between px-6 py-4">
        {/* Search */}
        <div className="flex-1 max-w-lg">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onCommandPaletteOpen}
            className="w-full flex items-center px-4 py-2.5 bg-gray-50 hover:bg-gray-100 rounded-xl border border-gray-200 transition-all duration-200 group"
          >
            <Search className="w-4 h-4 text-base-400 mr-3" />
            <span className="text-sm text-base-400 flex-1 text-left">
              Search or type a command...
            </span>
            <div className="flex items-center space-x-1 ml-3">
              <kbd className="px-2 py-1 text-xs font-medium text-base-500 bg-white rounded border border-gray-200 shadow-sm">
                <Command className="w-3 h-3 inline mr-1" />
                K
              </kbd>
            </div>
          </motion.button>
        </div>

        {/* Right side actions */}
        <div className="flex items-center space-x-3 ml-6">
          {/* Notifications */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="relative p-2.5 rounded-xl hover:bg-gray-100 transition-colors"
          >
            <Bell className="w-5 h-5 text-base-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-brand rounded-full"></span>
          </motion.button>

          {/* User menu */}
          <div className="relative">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
              className="flex items-center space-x-3 p-2 rounded-xl hover:bg-gray-100 transition-colors"
            >
              <div className="w-8 h-8 bg-brand rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="text-left hidden sm:block">
                <p className="text-sm font-medium text-base-900">John Doe</p>
                <p className="text-xs text-base-500">Portfolio Manager</p>
              </div>
            </motion.button>

            {/* User dropdown */}
            {isUserMenuOpen && (
              <motion.div
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                transition={{ duration: 0.2 }}
                className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50"
              >
                <div className="px-4 py-3 border-b border-gray-100">
                  <p className="text-sm font-medium text-base-900">John Doe</p>
                  <p className="text-xs text-base-500">john@company.com</p>
                </div>
                
                <div className="py-2">
                  <button className="w-full flex items-center px-4 py-2 text-sm text-base-700 hover:bg-gray-50 transition-colors">
                    <User className="w-4 h-4 mr-3" />
                    Profile
                  </button>
                  <button className="w-full flex items-center px-4 py-2 text-sm text-base-700 hover:bg-gray-50 transition-colors">
                    <Settings className="w-4 h-4 mr-3" />
                    Settings
                  </button>
                </div>
                
                <div className="border-t border-gray-100 pt-2">
                  <button className="w-full flex items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors">
                    <LogOut className="w-4 h-4 mr-3" />
                    Sign out
                  </button>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
} 