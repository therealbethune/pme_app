import React from 'react'

interface NeonCardProps {
  children: React.ReactNode
  className?: string
}

export const NeonCard: React.FC<NeonCardProps> = ({ children, className = '' }) => {
  return (
    <div 
      className={`
        relative rounded-2xl bg-bg-elevated p-6 shadow-md/5 
        transition-all duration-300 transform 
        hover:-translate-y-1 hover:shadow-neon-subtle
        group cursor-pointer
        ${className}
      `}
    >
      {/* Neon border effect on hover */}
      <div 
        className="
          absolute inset-0 rounded-2xl pointer-events-none opacity-0 
          group-hover:opacity-100 transition-opacity duration-300
          ring-2 ring-accent/40 blur-sm
        "
      />
      
      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  )
}

export default NeonCard 