import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from 'react-query'
import {
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
  LinearProgress,
} from '@mui/material'
import { School, CheckCircle } from '@mui/icons-material'
import { coursesAPI, progressAPI } from '../services/api'

const DifficultyChip = ({ difficulty }) => {
  const colors = {
    beginner: 'success',
    intermediate: 'warning',
    advanced: 'error',
  }
  return <Chip label={difficulty} color={colors[difficulty] || 'default'} size="small" />
}

const Modules = () => {
  const navigate = useNavigate()
  const { data: modulesData, isLoading } = useQuery('modules', () => coursesAPI.getModules())
  const { data: progressData } = useQuery('module-progress', progressAPI.getModuleProgress)

  if (isLoading) {
    return <LinearProgress />
  }

  const modules = modulesData?.data || []
  const progress = progressData?.data || []

  const getModuleProgress = (moduleId) => {
    return progress.find((p) => p.module.id === moduleId)
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Ansible Learning Modules
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Master Ansible through structured modules with hands-on exercises
      </Typography>

      <Grid container spacing={3}>
        {modules.map((module) => {
          const moduleProgress = getModuleProgress(module.id)
          const isCompleted = moduleProgress?.is_completed
          const completionPercentage = moduleProgress?.completion_percentage || 0

          return (
            <Grid item xs={12} sm={6} md={4} key={module.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  position: 'relative',
                }}
              >
                {isCompleted && (
                  <CheckCircle
                    sx={{
                      position: 'absolute',
                      top: 16,
                      right: 16,
                      color: 'success.main',
                    }}
                  />
                )}
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography variant="h5" component="div" gutterBottom>
                    {module.icon} {module.title}
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <DifficultyChip difficulty={module.difficulty} />
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {module.description}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      📚 {module.total_lessons} lessons
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      💻 {module.total_exercises} exercises
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      ⏱️ {module.estimated_hours}h
                    </Typography>
                  </Box>
                  {moduleProgress && (
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="caption">Progress</Typography>
                        <Typography variant="caption">{completionPercentage.toFixed(0)}%</Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={completionPercentage}
                        sx={{ height: 6, borderRadius: 1 }}
                      />
                    </Box>
                  )}
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    fullWidth
                    variant={moduleProgress?.is_started ? 'contained' : 'outlined'}
                    onClick={() => navigate(`/modules/${module.slug}`)}
                  >
                    {isCompleted ? 'Review' : moduleProgress?.is_started ? 'Continue' : 'Start Learning'}
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          )
        })}
      </Grid>
    </Box>
  )
}

export default Modules
