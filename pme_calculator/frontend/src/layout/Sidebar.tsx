import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ChevronLeft, 
  BarChart3, 
  Upload, 
  Settings, 
  Home,
  TrendingUp,
  PieChart,
  FileText
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface SidebarProps {
  className?: string
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Upload Data', href: '/upload', icon: Upload },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Performance', href: '/performance', icon: TrendingUp },
  { name: 'Portfolio', href: '/portfolio', icon: PieChart },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar({ className }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)

  return (
    <motion.aside
      initial={{ width: 256 }}
      animate={{ width: isCollapsed ? 80 : 256 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className={cn(
        'fixed left-0 top-0 z-40 h-screen bg-white border-r border-gray-200 shadow-sm',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <AnimatePresence mode="wait">
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
              className="flex items-center space-x-2"
            >
              <div className="w-8 h-8 bg-brand rounded-lg flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <span className="font-semibold text-base-900">PME Calculator</span>
            </motion.div>
          )}
        </AnimatePresence>
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <motion.div
            animate={{ rotate: isCollapsed ? 180 : 0 }}
            transition={{ duration: 0.3 }}
          >
            <ChevronLeft className="w-4 h-4 text-base-600" />
          </motion.div>
        </motion.button>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon
          return (
            <motion.a
              key={item.name}
              href={item.href}
              whileHover={{ x: 2 }}
              className={cn(
                'flex items-center px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
                'hover:bg-brand/5 hover:text-brand group',
                'text-base-600 hover:text-brand'
              )}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              
              <AnimatePresence mode="wait">
                {!isCollapsed && (
                  <motion.span
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    transition={{ duration: 0.2, delay: 0.1 }}
                    className="ml-3 truncate"
                  >
                    {item.name}
                  </motion.span>
                )}
              </AnimatePresence>
            </motion.a>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="absolute bottom-4 left-4 right-4">
        <AnimatePresence mode="wait">
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              transition={{ duration: 0.2 }}
              className="p-3 bg-brand/5 rounded-xl border border-brand/10"
            >
              <div className="flex items-center space-x-2">
                <div className="w-6 h-6 bg-brand/20 rounded-full flex items-center justify-center">
                  <TrendingUp className="w-3 h-3 text-brand" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-base-900 truncate">
                    Performance Ready
                  </p>
                  <p className="text-xs text-base-600 truncate">
                    4x faster analytics
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.aside>
  )
} 