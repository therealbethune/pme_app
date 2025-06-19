import React from 'react'
import { motion } from 'framer-motion'

interface HeroHeaderProps {
  title: string
  subtitle: string
  ctaText: string
  onCtaClick: () => void
}

export const HeroHeader: React.FC<HeroHeaderProps> = ({
  title,
  subtitle,
  ctaText,
  onCtaClick
}) => {
  return (
    <section className="relative min-h-[80vh] bg-bg-base flex items-center justify-center overflow-hidden">
      {/* Radial gradient background */}
      <div className="absolute inset-0 opacity-50">
        <div 
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[75vw] h-[75vh] blur-3xl"
          style={{
            background: 'radial-gradient(circle, transparent 0%, #00cfff0d 60%, transparent 100%)'
          }}
        />
      </div>

      {/* Glass content container */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="relative max-w-3xl mx-auto backdrop-blur-lg bg-white/5 ring-1 ring-white/5 rounded-2xl p-12 space-y-6 text-center"
      >
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-5xl font-semibold text-text-primary tracking-tight leading-none"
        >
          {title}
        </motion.h1>
        
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="text-lg text-slate-400/80 max-w-2xl mx-auto leading-relaxed"
        >
          {subtitle}
        </motion.p>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.6 }}
          className="pt-4"
        >
          <button
            onClick={onCtaClick}
            className="bg-accent hover:bg-accent/80 text-bg-base font-medium px-8 py-4 rounded-xl shadow-neon hover:shadow-neon-lg transition-all duration-300 transform hover:scale-105"
          >
            {ctaText}
          </button>
        </motion.div>
      </motion.div>
    </section>
  )
}

export default HeroHeader 