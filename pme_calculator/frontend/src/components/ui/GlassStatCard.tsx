import React, { useEffect, useState } from 'react'
import { useInView } from 'react-intersection-observer'
import { LucideIcon } from 'lucide-react'

interface GlassStatCardProps {
  label: string
  value: number
  suffix?: string
  prefix?: string
  delta?: {
    value: number
    isPositive: boolean
  }
  icon: LucideIcon
  className?: string
}

const useCountUp = (end: number, start: number = 0, duration: number = 800) => {
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
      
      setCount(currentCount)
      
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

export const GlassStatCard: React.FC<GlassStatCardProps> = ({
  label,
  value,
  suffix = '',
  prefix = '',
  delta,
  icon: Icon,
  className = ''
}) => {
  const { ref, inView } = useInView({
    threshold: 0.3,
    triggerOnce: true
  })
  
  const { count, setIsActive } = useCountUp(value, 0, 800)

  useEffect(() => {
    if (inView) {
      setIsActive(true)
    }
  }, [inView, setIsActive])

  const formatValue = (num: number) => {
    if (suffix === '%') {
      return num.toFixed(1)
    }
    if (suffix === 'x') {
      return num.toFixed(2)
    }
    if (suffix === 'M' || suffix === 'B') {
      return Math.floor(num).toLocaleString()
    }
    return Math.floor(num).toLocaleString()
  }

  return (
    <div
      ref={ref}
      className={`
        relative rounded-2xl backdrop-blur-sm
        ring-1 ring-white/10 p-6 w-44 h-36 
        flex flex-col justify-between text-gray-100
        shadow-xl transition-all duration-300 
        hover:shadow-2xl hover:-translate-y-1
        bg-black/20
        ${className}
      `}
    >
      {/* Icon */}
      <div className="flex justify-between items-start">
        <div className="text-sm font-medium text-gray-300">
          {label}
        </div>
        <Icon size={18} className="text-gray-400" />
      </div>
      
      {/* Value */}
      <div className="flex-1 flex items-center">
        <span className="text-2xl font-semibold text-gray-100">
          {prefix}{formatValue(count)}{suffix}
        </span>
      </div>
      
      {/* Delta pill */}
      {delta && (
        <div 
          className={`
            absolute bottom-4 right-4 rounded-full px-2 py-0.5 
            text-xs font-medium
            ${delta.isPositive 
              ? 'bg-green-500/20 text-green-400' 
              : 'bg-red-500/20 text-red-400'
            }
          `}
        >
          {delta.isPositive ? '+' : ''}{delta.value}%
        </div>
      )}
    </div>
  )
}

export default GlassStatCard 