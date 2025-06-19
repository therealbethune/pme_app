import React from 'react'
import { LucideIcon } from 'lucide-react'

interface GlowRingButtonProps {
  icon: LucideIcon
  onClick?: () => void
  className?: string
  size?: 'sm' | 'md' | 'lg'
  tooltip?: string
}

export const GlowRingButton: React.FC<GlowRingButtonProps> = ({ 
  icon: Icon,
  onClick, 
  className = '',
  size = 'md',
  tooltip
}) => {
  const sizeClasses = {
    sm: 'h-10 w-10',
    md: 'h-12 w-12',
    lg: 'h-14 w-14'
  }

  const iconSizes = {
    sm: 16,
    md: 18,
    lg: 20
  }

  return (
    <button
      onClick={onClick}
      title={tooltip}
      className={`
        relative inline-flex items-center justify-center 
        ${sizeClasses[size]} rounded-full bg-accent text-bg-base
        font-medium transition-all duration-300
        hover:bg-accent/90 hover:scale-105 hover:shadow-neon-lg
        focus:outline-none focus:ring-2 focus:ring-accent/50
        shadow-neon
        ${className}
      `}
    >
      {/* Animated glow ring */}
      <div 
        className="
          absolute -inset-1 rounded-full 
          border-2 border-accent-soft 
          animate-spin-slow pointer-events-none
        "
      />
      
      {/* Inner glow ring */}
      <div 
        className="
          absolute -inset-0.5 rounded-full 
          border border-accent/30 
          pointer-events-none
        "
      />
      
      {/* Button content */}
      <div className="relative z-10">
        <Icon size={iconSizes[size]} />
      </div>
    </button>
  )
}

export default GlowRingButton 