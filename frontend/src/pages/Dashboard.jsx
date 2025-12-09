import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from 'react-query'
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Button,
  Paper,
  Avatar,
  Chip,
} from '@mui/material'
import {
  TrendingUp,
  School,
  Assignment,
  EmojiEvents,
  LocalFireDepartment,
} from '@mui/icons-material'
import { progressAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

const StatCard = ({ title, value, icon, color, subtitle }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Avatar sx={{ bgcolor: color, mr: 2 }}>{icon}</Avatar>
        <Box>
          <Typography variant="h4" component="div">
            {value}
          </Typography>
          <Typography color="text.secondary" variant="body2">
            {title}
          </Typography>
        </Box>
      </Box>
      {subtitle && (
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
      )}
    </CardContent>
  </Card>
)

const Dashboard = () => {
  const navigate = useNavigate()
  const { user } = useAuth()

  const { data: overview, isLoading } = useQuery('progress-overview', progressAPI.getOverview)
  const { data: streakData } = useQuery('streak', progressAPI.getStreak)

  if (isLoading) {
    return <LinearProgress />
  }

  const stats = overview?.data
  const streak = streakData?.data

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Welcome back, {user?.username}! 👋
      </Typography>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Your Level"
            value={stats?.user_level || 1}
            icon={<TrendingUp />}
            color="primary.main"
            subtitle={`${stats?.user_xp || 0} XP`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Completed Lessons"
            value={stats?.lessons?.completed || 0}
            icon={<School />}
            color="success.main"
            subtitle={`${stats?.lessons?.completion_rate?.toFixed(1) || 0}% complete`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Exercises Passed"
            value={stats?.exercises?.passed || 0}
            icon={<Assignment />}
            color="info.main"
            subtitle={`${stats?.exercises?.success_rate?.toFixed(1) || 0}% success rate`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Day Streak"
            value={streak?.current_streak || 0}
            icon={<LocalFireDepartment />}
            color="error.main"
            subtitle={`Best: ${streak?.longest_streak || 0} days`}
          />
        </Grid>
      </Grid>

      {/* Progress Section */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Your Progress
            </Typography>
            
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Modules</Typography>
                <Typography variant="body2">
                  {stats?.modules?.completed || 0} / {stats?.modules?.total || 0}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={stats?.modules?.completion_rate || 0}
                sx={{ height: 8, borderRadius: 1 }}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Lessons</Typography>
                <Typography variant="body2">
                  {stats?.lessons?.completed || 0} / {stats?.lessons?.total || 0}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={stats?.lessons?.completion_rate || 0}
                sx={{ height: 8, borderRadius: 1 }}
                color="success"
              />
            </Box>

            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Level Progress</Typography>
                <Typography variant="body2">
                  {user?.total_xp || 0} / {(user?.level || 1) * 1000} XP
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={user?.progress_percentage || 0}
                sx={{ height: 8, borderRadius: 1 }}
                color="secondary"
              />
            </Box>

            <Box sx={{ mt: 3 }}>
              <Button
                variant="contained"
                fullWidth
                onClick={() => navigate('/modules')}
                size="large"
              >
                Continue Learning
              </Button>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Stats
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Time Spent Learning
                </Typography>
                <Typography variant="h6">
                  {stats?.time_spent_minutes || 0} minutes
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  In Progress
                </Typography>
                <Typography variant="h6">
                  {stats?.modules?.in_progress || 0} modules
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Total Attempts
                </Typography>
                <Typography variant="h6">
                  {stats?.exercises?.attempted || 0} exercises
                </Typography>
              </Box>
            </Box>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Achievement
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <EmojiEvents sx={{ fontSize: 48, color: 'gold' }} />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Keep up the great work!
                </Typography>
                <Button size="small" onClick={() => navigate('/profile')}>
                  View All
                </Button>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
