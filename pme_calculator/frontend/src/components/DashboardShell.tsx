import React from 'react'
import { motion } from 'framer-motion'
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Container,
  Divider,
  Chip,
  Stack,
  Paper
} from '@mui/material'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Activity,
  BarChart3,
  PieChart,
  Users,
  Target,
  Clock,
  Award
} from 'lucide-react'
import { Sidebar } from '../layout/Sidebar'
import { Header } from '../layout/Header'
import { KpiCard } from '../lib/ui/KpiCard'
import { CommandModal } from './CommandModal'

const DashboardShell: React.FC = () => {
  const [commandOpen, setCommandOpen] = React.useState(false)

  // Sample KPI data showcasing the design system
  const kpiData = [
    {
      title: 'Total AUM',
      value: '$2.4B',
      change: { value: '+12.5%', trend: 'up' as const },
      icon: DollarSign
    },
    {
      title: 'Portfolio IRR',
      value: '15.2%',
      change: { value: '+2.1%', trend: 'up' as const },
      icon: TrendingUp
    },
    {
      title: 'Active Funds',
      value: '24',
      change: { value: '+3', trend: 'up' as const },
      icon: PieChart
    },
    {
      title: 'PME Ratio',
      value: '1.18x',
      change: { value: '-0.02x', trend: 'down' as const },
      icon: Activity
    },
    {
      title: 'Net TVPI',
      value: '1.45x',
      change: { value: '+0.08x', trend: 'up' as const },
      icon: BarChart3
    },
    {
      title: 'Vintage Years',
      value: '2019-2024',
      change: { value: '5 years', trend: 'neutral' as const },
      icon: Target
    },
    {
      title: 'LP Count',
      value: '127',
      change: { value: '+8', trend: 'up' as const },
      icon: Users
    },
    {
      title: 'Deployment',
      value: '78%',
      change: { value: '+5%', trend: 'up' as const },
      icon: TrendingUp
    }
  ]

  // Recent activity data
  const recentActivities = [
    { label: 'Fund Analysis Complete', time: '2 min ago', type: 'success' },
    { label: 'New LP Onboarded', time: '1 hour ago', type: 'info' },
    { label: 'Quarterly Report Generated', time: '3 hours ago', type: 'default' },
    { label: 'PME Calculation Updated', time: '1 day ago', type: 'warning' }
  ]

  // Keyboard shortcut handler
  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault()
        setCommandOpen(true)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Header onCommandPaletteOpen={() => setCommandOpen(true)} />
        
        {/* Dashboard Content */}
        <Container 
          maxWidth="xl" 
          sx={{ 
            flex: 1, 
            py: 4,
            px: { xs: 2, sm: 3, md: 4 }
          }}
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            {/* Hero Section */}
            <Box sx={{ mb: 6 }}>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1, duration: 0.6 }}
              >
                <Typography 
                  variant="h3" 
                  sx={{ 
                    fontWeight: 800,
                    fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' },
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    mb: 2
                  }}
                >
                  Portfolio Dashboard
                </Typography>
                <Typography 
                  variant="h6"
                  sx={{ 
                    color: 'text.secondary',
                    fontWeight: 400,
                    maxWidth: '600px',
                    lineHeight: 1.6
                  }}
                >
                  Professional-grade PME Calculator with advanced analytics and modern design
                </Typography>
              </motion.div>
            </Box>

            {/* KPI Grid */}
            <Box 
              sx={{ 
                display: 'grid', 
                gridTemplateColumns: {
                  xs: '1fr',
                  sm: 'repeat(2, 1fr)',
                  md: 'repeat(3, 1fr)',
                  lg: 'repeat(4, 1fr)'
                },
                gap: { xs: 2, sm: 3, md: 4 },
                mb: 6
              }}
            >
              {kpiData.map((kpi, index) => (
                <motion.div
                  key={kpi.title}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ 
                    delay: 0.1 * index, 
                    duration: 0.6,
                    ease: "easeOut"
                  }}
                >
                  <KpiCard {...kpi} />
                </motion.div>
              ))}
            </Box>

            {/* Main Content Grid */}
            <Box 
              sx={{ 
                display: 'grid', 
                gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' }, 
                gap: { xs: 3, md: 4 }
              }}
            >
              {/* Performance Analytics Card */}
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5, duration: 0.6 }}
              >
                <Card 
                  sx={{ 
                    height: '100%',
                    borderRadius: 3,
                    border: '1px solid',
                    borderColor: 'divider',
                    background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%)',
                    backdropFilter: 'blur(20px)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 12px 40px rgba(0,0,0,0.08)',
                    }
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                      <Box
                        sx={{
                          p: 1.5,
                          borderRadius: 2,
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        }}
                      >
                        <BarChart3 size={24} color="white" />
                      </Box>
                      <Typography 
                        variant="h5" 
                        sx={{ 
                          fontWeight: 700,
                          color: 'text.primary'
                        }}
                      >
                        Performance Analytics
                      </Typography>
                    </Box>
                    
                    <Box 
                      sx={{ 
                        height: 320,
                        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
                        borderRadius: 2,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        border: '2px dashed',
                        borderColor: 'divider'
                      }}
                    >
                      <Stack alignItems="center" spacing={2}>
                        <Award size={48} color="#667eea" />
                        <Typography 
                          variant="h6" 
                          sx={{ 
                            color: 'text.secondary',
                            fontWeight: 500
                          }}
                        >
                          Chart Visualization Area
                        </Typography>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            color: 'text.secondary',
                            textAlign: 'center',
                            maxWidth: 300
                          }}
                        >
                          Interactive charts and performance metrics will be displayed here
                        </Typography>
                      </Stack>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Recent Activity Panel */}
              <motion.div
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6, duration: 0.6 }}
              >
                <Card 
                  sx={{ 
                    height: '100%',
                    borderRadius: 3,
                    border: '1px solid',
                    borderColor: 'divider',
                    background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%)',
                    backdropFilter: 'blur(20px)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 12px 40px rgba(0,0,0,0.08)',
                    }
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                      <Box
                        sx={{
                          p: 1.5,
                          borderRadius: 2,
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        }}
                      >
                        <Clock size={24} color="white" />
                      </Box>
                      <Typography 
                        variant="h5" 
                        sx={{ 
                          fontWeight: 700,
                          color: 'text.primary'
                        }}
                      >
                        Recent Activity
                      </Typography>
                    </Box>
                    
                    <Stack spacing={3}>
                      {recentActivities.map((activity, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.7 + (index * 0.1), duration: 0.4 }}
                        >
                          <Paper
                            sx={{
                              p: 2.5,
                              borderRadius: 2,
                              border: '1px solid',
                              borderColor: 'divider',
                              background: 'rgba(255,255,255,0.7)',
                              transition: 'all 0.2s ease',
                              '&:hover': {
                                background: 'rgba(255,255,255,0.9)',
                                transform: 'translateX(4px)',
                              }
                            }}
                          >
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <Box
                                sx={{
                                  width: 8,
                                  height: 8,
                                  borderRadius: '50%',
                                  bgcolor: activity.type === 'success' ? 'success.main' :
                                          activity.type === 'info' ? 'info.main' :
                                          activity.type === 'warning' ? 'warning.main' : 'grey.400'
                                }}
                              />
                              <Box sx={{ flex: 1 }}>
                                <Typography 
                                  variant="body2" 
                                  sx={{ 
                                    fontWeight: 600,
                                    color: 'text.primary',
                                    mb: 0.5
                                  }}
                                >
                                  {activity.label}
                                </Typography>
                                <Typography 
                                  variant="caption" 
                                  sx={{ 
                                    color: 'text.secondary',
                                    fontSize: '0.75rem'
                                  }}
                                >
                                  {activity.time}
                                </Typography>
                              </Box>
                            </Box>
                          </Paper>
                        </motion.div>
                      ))}
                    </Stack>
                  </CardContent>
                </Card>
              </motion.div>
            </Box>
          </motion.div>
        </Container>
      </Box>

      {/* Command Modal */}
      <CommandModal isOpen={commandOpen} onClose={() => setCommandOpen(false)} />
    </Box>
  )
}

export default DashboardShell 