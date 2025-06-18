import { describe, it, expect } from 'vitest'

// Simple utility functions to test
const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value)
}

const calculatePercentage = (value: number, total: number): number => {
  if (total === 0) return 0
  return (value / total) * 100
}

describe('Utility Functions', () => {
  describe('formatCurrency', () => {
    it('formats positive numbers correctly', () => {
      expect(formatCurrency(1000)).toBe('$1,000.00')
      expect(formatCurrency(1234.56)).toBe('$1,234.56')
    })

    it('formats negative numbers correctly', () => {
      expect(formatCurrency(-500)).toBe('-$500.00')
    })

    it('formats zero correctly', () => {
      expect(formatCurrency(0)).toBe('$0.00')
    })
  })

  describe('calculatePercentage', () => {
    it('calculates percentage correctly', () => {
      expect(calculatePercentage(25, 100)).toBe(25)
      expect(calculatePercentage(1, 4)).toBe(25)
    })

    it('handles zero total', () => {
      expect(calculatePercentage(10, 0)).toBe(0)
    })

    it('handles zero value', () => {
      expect(calculatePercentage(0, 100)).toBe(0)
    })
  })
}) 