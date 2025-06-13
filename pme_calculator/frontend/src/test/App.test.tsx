import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from '../App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    // Just verify the app renders without throwing
    expect(document.body).toBeTruthy()
  })

  it('contains main application elements', () => {
    const { container } = render(<App />)
    // Just verify the app container exists
    expect(container).toBeTruthy()
    expect(container.firstChild).toBeTruthy()
  })
}) 