import React from 'react'
import { useQuery } from 'react-query'
import {
  Box,
  Typography,
  Paper,
  Grid,
  Avatar,
  Chip,
  LinearProgress,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material'
import { EmojiEvents, TrendingUp } from '@mui/icons-material'
import { useAuth } from '../context/AuthContext'
import { authAPI, progressAPI } from '../services/api'

const Profile = () => {
  const { user } = useAuth()
  const { data: statsData } = useQuery('user-stats', authAPI.getStats)
  const { data: achievementsData } = useQuery('achievements', authAPI.getAchievements)

  const stats = statsData?.data
  const achievements = achievementsData?.data || []

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Profile
      </Typography>

      <Grid container spacing={3}>
        {/* User Info */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Avatar
              src={user?.avatar}
              sx={{ width: 120, height: 120, mx: 'auto', mb: 2 }}
            >
              {user?.username?.[0]?.toUpperCase()}
            </Avatar>
            <Typography variant="h5" gutterBottom>
              {user?.username}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {user?.email}
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mt: 2 }}>
              <Chip label={`Level ${user?.level}`} color="primary" icon={<TrendingUp />} />
              <Chip label={`${user?.total_xp} XP`} variant="outlined" />
            </Box>
            {user?.bio && (
              <Typography variant="body2" sx={{ mt: 2 }}>
                {user.bio}
              </Typography>
            )}
          </Paper>

          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Level Progress
            </Typography>
            <Box sx={{ mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                {user?.xp_to_next_level} XP to Level {(user?.level || 0) + 1}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={user?.progress_percentage || 0}
              sx={{ height: 10, borderRadius: 1 }}
            />
          </Paper>
        </Grid>

        {/* Stats */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h4" color="primary">
                      {stats?.statistics?.completed_lessons || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Lessons Completed
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h4" color="success.main">
                      {stats?.statistics?.completed_exercises || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Exercises Passed
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h4" color="info.main">
                      {stats?.statistics?.total_attempts || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Attempts
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h4" color="warning.main">
                      {stats?.statistics?.achievements_unlocked || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Achievements
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>

          {/* Achievements */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              <EmojiEvents sx={{ verticalAlign: 'middle', mr: 1 }} />
              All Achievements
            </Typography>
            {achievements.length > 0 ? (
              <List>
                {achievements.map((achievement) => (
                  <ListItem key={achievement.id}>
                    <ListItemIcon>
                      <Typography variant="h4">{achievement.icon}</Typography>
                    </ListItemIcon>
                    <ListItemText
                      primary={achievement.name}
                      secondary={
                        <>
                          {achievement.description}
                          <br />
                          <Chip
                            label={`${achievement.xp_reward} XP`}
                            size="small"
                            sx={{ mt: 0.5 }}
                          />
                        </>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Start learning to unlock achievements!
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Profile
