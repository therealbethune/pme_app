import React, { useState, useEffect, useRef } from 'react'
import { Search, FileText, BarChart3, Upload, Settings, HelpCircle } from 'lucide-react'

interface CommandItem {
  id: string
  title: string
  description: string
  icon: React.ComponentType<any>
  action: () => void
  category: string
}

interface CommandPaletteProps {
  isOpen: boolean
  onClose: () => void
}

const commands: CommandItem[] = [
  {
    id: 'analysis',
    title: 'View Analysis',
    description: 'Open performance analysis dashboard',
    icon: BarChart3,
    action: () => window.location.href = '/analysis',
    category: 'Navigation'
  },
  {
    id: 'upload',
    title: 'Upload Data',
    description: 'Upload new portfolio data files',
    icon: Upload,
    action: () => window.location.href = '/upload',
    category: 'Actions'
  },
  {
    id: 'enhanced',
    title: 'Enhanced Dashboard',
    description: 'View the enhanced neon dashboard',
    icon: BarChart3,
    action: () => window.location.href = '/enhanced',
    category: 'Navigation'
  },
  {
    id: 'charts',
    title: 'Charts Test',
    description: 'View chart testing interface',
    icon: BarChart3,
    action: () => window.location.href = '/charts-test',
    category: 'Navigation'
  },
  {
    id: 'help',
    title: 'Help & Documentation',
    description: 'Get help and view documentation',
    icon: HelpCircle,
    action: () => console.log('Help clicked'),
    category: 'Support'
  }
]

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const filteredCommands = commands.filter(command =>
    command.title.toLowerCase().includes(query.toLowerCase()) ||
    command.description.toLowerCase().includes(query.toLowerCase()) ||
    command.category.toLowerCase().includes(query.toLowerCase())
  )

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  useEffect(() => {
    setSelectedIndex(0)
  }, [query])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return

      switch (e.key) {
        case 'Escape':
          onClose()
          break
        case 'ArrowDown':
          e.preventDefault()
          setSelectedIndex(prev => 
            prev < filteredCommands.length - 1 ? prev + 1 : 0
          )
          break
        case 'ArrowUp':
          e.preventDefault()
          setSelectedIndex(prev => 
            prev > 0 ? prev - 1 : filteredCommands.length - 1
          )
          break
        case 'Enter':
          e.preventDefault()
          if (filteredCommands[selectedIndex]) {
            filteredCommands[selectedIndex].action()
            onClose()
          }
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, selectedIndex, filteredCommands, onClose])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-[#0d0d0d]/80 backdrop-blur-[2px]"
        onClick={onClose}
      />
      
      {/* Command Panel */}
      <div className="relative w-96 bg-bg-raised rounded-3xl p-4 ring-1 ring-accent-soft shadow-neon-lg">
        {/* Search Input */}
        <div className="relative mb-4">
          <Search size={18} className="absolute left-4 top-1/2 transform -translate-y-1/2 text-fg-muted" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search commands..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-bg-base rounded-2xl border border-accent-soft text-fg-primary placeholder-fg-muted focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent transition-all duration-200"
          />
        </div>

        {/* Results */}
        <div className="max-h-80 overflow-y-auto">
          {filteredCommands.length === 0 ? (
            <div className="text-center py-8 text-fg-muted">
              <FileText size={32} className="mx-auto mb-3 opacity-50" />
              <p>No commands found</p>
            </div>
          ) : (
            <div className="space-y-1">
              {filteredCommands.map((command, index) => {
                const Icon = command.icon
                return (
                  <button
                    key={command.id}
                    onClick={() => {
                      command.action()
                      onClose()
                    }}
                    className={`
                      w-full flex items-center gap-4 p-3 rounded-2xl text-left transition-all duration-200
                      ${index === selectedIndex 
                        ? 'bg-accent/10 ring-1 ring-accent/30 text-fg-primary' 
                        : 'hover:bg-bg-base text-fg-muted hover:text-fg-primary'
                      }
                    `}
                  >
                    <div className={`
                      p-2 rounded-xl
                      ${index === selectedIndex ? 'bg-accent/20' : 'bg-bg-base'}
                    `}>
                      <Icon size={16} className={index === selectedIndex ? 'text-accent' : 'text-fg-muted'} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">
                        {command.title}
                      </div>
                      <div className="text-sm text-fg-muted truncate">
                        {command.description}
                      </div>
                    </div>
                    <div className="text-xs text-fg-muted bg-bg-base px-2 py-1 rounded-lg">
                      {command.category}
                    </div>
                  </button>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-4 pt-4 border-t border-accent-soft flex items-center justify-between text-xs text-fg-muted">
          <div className="flex items-center gap-4">
            <kbd className="px-2 py-1 bg-bg-base rounded border border-accent-soft">↑↓</kbd>
            <span>Navigate</span>
          </div>
          <div className="flex items-center gap-4">
            <kbd className="px-2 py-1 bg-bg-base rounded border border-accent-soft">↵</kbd>
            <span>Select</span>
          </div>
          <div className="flex items-center gap-4">
            <kbd className="px-2 py-1 bg-bg-base rounded border border-accent-soft">Esc</kbd>
            <span>Close</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CommandPalette 