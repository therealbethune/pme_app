import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface KpiCardProps {
  title: string
  value: string | number
  change?: {
    value: string | number
    trend: 'up' | 'down' | 'neutral'
  }
  icon?: LucideIcon
  className?: string
  delay?: number
}

export function KpiCard({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  className, 
  delay = 0 
}: KpiCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.5, 
        delay,
        ease: [0.21, 1.11, 0.81, 0.99]
      }}
      whileHover={{ 
        y: -2,
        transition: { duration: 0.2 }
      }}
      className={cn(
        'relative bg-white rounded-2xl shadow-sm border border-gray-200 p-6',
        'hover:shadow-lg transition-all duration-300',
        // Electric blue left border accent
        'border-l-4 border-l-brand',
        className
      )}
    >
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-brand/[0.02] to-transparent rounded-2xl" />
      
      <div className="relative">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-base-600 truncate">
            {title}
          </h3>
          {Icon && (
            <motion.div
              whileHover={{ scale: 1.1, rotate: 5 }}
              className="p-2 bg-brand/10 rounded-lg"
            >
              <Icon className="w-4 h-4 text-brand" />
            </motion.div>
          )}
        </div>

        {/* Value */}
        <motion.div
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ delay: delay + 0.2, duration: 0.3 }}
          className="mb-2"
        >
          <p className="text-2xl font-bold text-base-900 tracking-tight">
            {value}
          </p>
        </motion.div>

        {/* Change indicator */}
        {change && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: delay + 0.3, duration: 0.3 }}
            className="flex items-center"
          >
            <span className={cn(
              'text-xs font-medium px-2 py-1 rounded-full',
              change.trend === 'up' && 'text-green-700 bg-green-100',
              change.trend === 'down' && 'text-red-700 bg-red-100',
              change.trend === 'neutral' && 'text-base-700 bg-base-100'
            )}>
              {change.trend === 'up' && '↗'}
              {change.trend === 'down' && '↘'}
              {change.trend === 'neutral' && '→'}
              {' '}
              {change.value}
            </span>
          </motion.div>
        )}
      </div>

      {/* Hover effect overlay */}
      <motion.div
        className="absolute inset-0 rounded-2xl bg-gradient-to-r from-brand/5 to-transparent opacity-0"
        whileHover={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      />
    </motion.div>
  )
} 