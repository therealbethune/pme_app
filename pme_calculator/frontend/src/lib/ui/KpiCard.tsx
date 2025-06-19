import React from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, Box, Typography, Chip } from '@mui/material'
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '@/lib/utils'

interface KpiCardProps {
  title: string
  value: string
  change?: {
    value: string
    trend: 'up' | 'down' | 'neutral'
  }
  icon: LucideIcon
  className?: string
  delay?: number
}

export const KpiCard: React.FC<KpiCardProps> = ({ title, value, change, icon: Icon, className, delay = 0 }) => {
  const getTrendIcon = () => {
    switch (change?.trend) {
      case 'up': return TrendingUp
      case 'down': return TrendingDown
      default: return Minus
    }
  }

  const getTrendColor = () => {
    switch (change?.trend) {
      case 'up': return 'success'
      case 'down': return 'error'
      default: return 'default'
    }
  }

  const TrendIcon = getTrendIcon()

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
        y: -4,
        transition: { duration: 0.2 }
      }}
      whileTap={{ scale: 0.98 }}
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
      
      <Card 
        sx={{ 
          height: '100%',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 3,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
            borderColor: 'primary.light',
          }
        }}
      >
        <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
          {/* Header with Icon */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography 
              variant="body2" 
              sx={{ 
                color: 'text.secondary',
                fontWeight: 500,
                fontSize: '0.875rem',
                letterSpacing: '0.025em'
              }}
            >
              {title}
            </Typography>
            <Box
              sx={{
                p: 1,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Icon size={18} color="white" />
            </Box>
          </Box>

          {/* Main Value */}
          <Typography 
            variant="h4" 
            sx={{ 
              fontWeight: 700,
              fontSize: { xs: '1.75rem', sm: '2rem' },
              lineHeight: 1.2,
              mb: 2,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            {value}
          </Typography>

          {/* Change Indicator */}
          {change && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                icon={<TrendIcon size={14} />}
                label={change.value}
                size="small"
                color={getTrendColor() as any}
                variant="outlined"
                sx={{
                  height: 24,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  borderRadius: 1.5,
                  '& .MuiChip-icon': {
                    marginLeft: '6px',
                    marginRight: '-2px',
                  },
                  ...(change.trend === 'up' && {
                    color: 'success.main',
                    borderColor: 'success.main',
                    backgroundColor: 'rgba(46, 125, 50, 0.08)',
                  }),
                  ...(change.trend === 'down' && {
                    color: 'error.main',
                    borderColor: 'error.main',
                    backgroundColor: 'rgba(211, 47, 47, 0.08)',
                  }),
                  ...(change.trend === 'neutral' && {
                    color: 'text.secondary',
                    borderColor: 'divider',
                    backgroundColor: 'action.hover',
                  }),
                }}
              />
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Hover effect overlay */}
      <motion.div
        className="absolute inset-0 rounded-2xl bg-gradient-to-r from-brand/5 to-transparent opacity-0"
        whileHover={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      />
    </motion.div>
  )
} 