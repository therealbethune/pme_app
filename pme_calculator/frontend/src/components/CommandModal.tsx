import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Search, 
  Home, 
  Upload, 
  BarChart3, 
  TrendingUp, 
  PieChart, 
  FileText, 
  Settings,
  X
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface CommandModalProps {
  isOpen: boolean
  onClose: () => void
}

const commands = [
  { id: 'dashboard', name: 'Dashboard', description: 'Go to main dashboard', icon: Home, href: '/' },
  { id: 'upload', name: 'Upload Data', description: 'Upload fund and index data', icon: Upload, href: '/upload' },
  { id: 'analytics', name: 'Analytics', description: 'View detailed analytics', icon: BarChart3, href: '/analytics' },
  { id: 'performance', name: 'Performance', description: 'Performance metrics', icon: TrendingUp, href: '/performance' },
  { id: 'portfolio', name: 'Portfolio', description: 'Portfolio overview', icon: PieChart, href: '/portfolio' },
  { id: 'reports', name: 'Reports', description: 'Generate reports', icon: FileText, href: '/reports' },
  { id: 'settings', name: 'Settings', description: 'Application settings', icon: Settings, href: '/settings' },
]

export function CommandModal({ isOpen, onClose }: CommandModalProps) {
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)

  const filteredCommands = commands.filter(command =>
    command.name.toLowerCase().includes(query.toLowerCase()) ||
    command.description.toLowerCase().includes(query.toLowerCase())
  )

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return

      if (e.key === 'Escape') {
        onClose()
      } else if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex(prev => 
          prev < filteredCommands.length - 1 ? prev + 1 : 0
        )
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex(prev => 
          prev > 0 ? prev - 1 : filteredCommands.length - 1
        )
      } else if (e.key === 'Enter') {
        e.preventDefault()
        if (filteredCommands[selectedIndex]) {
          // Navigate to the selected command
          window.location.href = filteredCommands[selectedIndex].href
          onClose()
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, filteredCommands, selectedIndex, onClose])

  useEffect(() => {
    setSelectedIndex(0)
  }, [query])

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm"
        onClick={onClose}
      >
        <div className="flex items-start justify-center pt-[10vh] px-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{ duration: 0.2 }}
            className="w-full max-w-2xl bg-white rounded-xl shadow-card border border-gray-200 overflow-hidden"
            onClick={e => e.stopPropagation()}
          >
            {/* Search input */}
            <div className="flex items-center px-4 py-4 border-b border-gray-200">
              <Search className="w-5 h-5 text-base-400 mr-3" />
              <input
                type="text"
                placeholder="Search commands..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="flex-1 bg-transparent text-base-900 placeholder-base-400 outline-none text-lg"
                autoFocus
              />
              <button
                onClick={onClose}
                className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <X className="w-4 h-4 text-base-400" />
              </button>
            </div>

            {/* Results */}
            <div className="max-h-96 overflow-y-auto">
              {filteredCommands.length === 0 ? (
                <div className="px-4 py-8 text-center">
                  <p className="text-base-500">No commands found</p>
                </div>
              ) : (
                <div className="py-2">
                  {filteredCommands.map((command, index) => {
                    const Icon = command.icon
                    return (
                      <motion.button
                        key={command.id}
                        whileHover={{ backgroundColor: 'rgba(24, 119, 255, 0.05)' }}
                        className={cn(
                          'w-full flex items-center px-4 py-3 text-left transition-colors',
                          index === selectedIndex 
                            ? 'bg-brand/5 border-r-2 border-r-brand' 
                            : 'hover:bg-gray-50'
                        )}
                        onClick={() => {
                          window.location.href = command.href
                          onClose()
                        }}
                      >
                        <div className={cn(
                          'p-2 rounded-lg mr-3',
                          index === selectedIndex 
                            ? 'bg-brand/10 text-brand' 
                            : 'bg-gray-100 text-base-600'
                        )}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className={cn(
                            'font-medium truncate',
                            index === selectedIndex 
                              ? 'text-brand' 
                              : 'text-base-900'
                          )}>
                            {command.name}
                          </p>
                          <p className="text-sm text-base-500 truncate">
                            {command.description}
                          </p>
                        </div>
                      </motion.button>
                    )
                  })}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between text-xs text-base-500">
                <div className="flex items-center space-x-4">
                  <span>↑↓ Navigate</span>
                  <span>↵ Select</span>
                  <span>esc Close</span>
                </div>
                <span>Ctrl+K to open</span>
              </div>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </AnimatePresence>
  )
} 