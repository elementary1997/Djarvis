import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from 'react-query'
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
} from '@mui/material'
import { CheckCircle, Circle, PlayArrow } from '@mui/icons-material'
import { coursesAPI, progressAPI } from '../services/api'

const ModuleDetail = () => {
  const { slug } = useParams()
  const navigate = useNavigate()
  
  const { data: moduleData, isLoading } = useQuery(['module', slug], () =>
    coursesAPI.getModule(slug)
  )
  const { data: progressData } = useQuery('lesson-progress', progressAPI.getLessonProgress)

  if (isLoading) {
    return <LinearProgress />
  }

  const module = moduleData?.data
  const progress = progressData?.data || []

  const getLessonProgress = (lessonId) => {
    return progress.find((p) => p.lesson.id === lessonId)
  }

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          {module.icon} {module.title}
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Chip label={module.difficulty} color="primary" />
          <Chip label={`${module.total_lessons} lessons`} variant="outlined" />
          <Chip label={`${module.total_exercises} exercises`} variant="outlined" />
          <Chip label={`${module.estimated_hours}h`} variant="outlined" />
        </Box>
        <Typography variant="body1" color="text.secondary">
          {module.description}
        </Typography>
      </Box>

      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        Lessons
      </Typography>

      <Grid container spacing={2}>
        {module.lessons?.map((lesson, index) => {
          const lessonProgress = getLessonProgress(lesson.id)
          const isCompleted = lessonProgress?.is_completed

          return (
            <Grid item xs={12} key={lesson.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    {isCompleted ? (
                      <CheckCircle color="success" />
                    ) : (
                      <Circle color="disabled" />
                    )}
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6">
                        {index + 1}. {lesson.title}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          💻 {lesson.exercise_count} exercises
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          ⏱️ {lesson.estimated_minutes} min
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          ⭐ {lesson.xp_reward} XP
                        </Typography>
                      </Box>
                    </Box>
                    <Button
                      variant={isCompleted ? 'outlined' : 'contained'}
                      startIcon={<PlayArrow />}
                      onClick={() =>
                        navigate(`/modules/${slug}/lessons/${lesson.slug}`)
                      }
                    >
                      {isCompleted ? 'Review' : 'Start'}
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )
        })}
      </Grid>
    </Box>
  )
}

export default ModuleDetail
