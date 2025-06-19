import React from 'react'

interface ButtonGlowProps {
  children: React.ReactNode
  onClick?: () => void
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export const ButtonGlow: React.FC<ButtonGlowProps> = ({ 
  children, 
  onClick, 
  className = '',
  size = 'md'
}) => {
  const sizeClasses = {
    sm: 'h-10 w-10',
    md: 'h-14 w-14',
    lg: 'h-16 w-16'
  }

  return (
    <button
      onClick={onClick}
      className={`
        relative inline-flex items-center justify-center 
        ${sizeClasses[size]} rounded-full bg-accent text-bg-base
        font-medium transition-all duration-300
        hover:bg-accent/90 hover:scale-105
        focus:outline-none focus:ring-2 focus:ring-accent/50
        ${className}
      `}
    >
      {/* Animated glow ring */}
      <div 
        className="
          absolute -inset-1 rounded-full 
          border-2 border-accent/20 blur-sm 
          animate-spin-slow pointer-events-none
        "
      />
      
      {/* Button content */}
      <div className="relative z-10">
        {children}
      </div>
    </button>
  )
}

export default ButtonGlow 