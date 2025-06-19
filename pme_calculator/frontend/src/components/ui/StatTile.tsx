import React, { useEffect, useState } from 'react'
import { useInView } from 'react-intersection-observer'
import { LucideIcon } from 'lucide-react'

interface StatTileProps {
  label: string
  valueFrom: number
  valueTo: number
  suffix?: string
  prefix?: string
  icon?: LucideIcon
  className?: string
}

const useCountUp = (end: number, start: number = 0, duration: number = 2000) => {
  const [count, setCount] = useState(start)
  const [isActive, setIsActive] = useState(false)

  useEffect(() => {
    if (!isActive) return

    let startTime: number
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime
      const progress = Math.min((currentTime - startTime) / duration, 1)
      
      const easeOutQuart = 1 - Math.pow(1 - progress, 4)
      const currentCount = start + (end - start) * easeOutQuart
      
      setCount(Math.floor(currentCount))
      
      if (progress < 1) {
        requestAnimationFrame(animate)
      } else {
        setCount(end)
      }
    }
    
    requestAnimationFrame(animate)
  }, [isActive, end, start, duration])

  return { count, setIsActive }
}

export const StatTile: React.FC<StatTileProps> = ({
  label,
  valueFrom,
  valueTo,
  suffix = '',
  prefix = '',
  icon: Icon,
  className = ''
}) => {
  const { ref, inView } = useInView({
    threshold: 0.3,
    triggerOnce: true
  })
  
  const { count, setIsActive } = useCountUp(valueTo, valueFrom, 2000)

  useEffect(() => {
    if (inView) {
      setIsActive(true)
    }
  }, [inView, setIsActive])

  return (
    <div
      ref={ref}
      className={`
        relative bg-bg-elevated rounded-xl px-8 py-6 
        shadow-inner/5 border border-white/5
        transition-all duration-300 hover:border-accent/20
        ${className}
      `}
    >
      {/* Icon */}
      {Icon && (
        <div className="flex items-center justify-between mb-4">
          <div className="p-2 bg-accent/10 rounded-lg">
            <Icon size={20} className="text-accent" />
          </div>
        </div>
      )}
      
      {/* Value */}
      <div className="mb-2">
        <span className="text-3xl font-bold text-text-primary">
          {prefix}{count.toLocaleString()}{suffix}
        </span>
      </div>
      
      {/* Label */}
      <div className="text-sm text-text-muted font-medium">
        {label}
      </div>
      
      {/* Neon underline sweep */}
      <div className="relative mt-4">
        <div 
          className={`
            absolute bottom-0 left-0 h-0.5 bg-accent 
            transition-all duration-700 ease-out
            ${inView ? 'w-full' : 'w-0'}
          `}
        />
      </div>
    </div>
  )
}

export default StatTile 