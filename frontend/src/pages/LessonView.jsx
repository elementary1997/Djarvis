import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from 'react-query'
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Alert,
} from '@mui/material'
import { CheckCircle, NavigateNext, NavigateBefore } from '@mui/icons-material'
import { coursesAPI, progressAPI, exercisesAPI } from '../services/api'
import MarkdownViewer from '../components/MarkdownViewer'

const LessonView = () => {
  const { moduleSlug, lessonSlug } = useParams()
  const navigate = useNavigate()
  const [completed, setCompleted] = useState(false)

  const { data: lessonData, isLoading } = useQuery(
    ['lesson', moduleSlug, lessonSlug],
    () => coursesAPI.getLesson(moduleSlug, lessonSlug)
  )

  const { data: exercisesData } = useQuery(
    ['exercises', lessonData?.data?.id],
    () => exercisesAPI.getExercises({ lesson: lessonData?.data?.id }),
    { enabled: !!lessonData?.data?.id }
  )

  const markCompleteMutation = useMutation(
    () => progressAPI.markLessonComplete({ lesson_id: lessonData?.data?.id }),
    {
      onSuccess: () => {
        setCompleted(true)
      },
    }
  )

  if (isLoading) {
    return <LinearProgress />
  }

  const lesson = lessonData?.data
  const exercises = exercisesData?.data || []

  const handleComplete = () => {
    markCompleteMutation.mutate()
  }

  const handleStartExercise = (exerciseId) => {
    navigate(`/exercises/${exerciseId}`)
  }

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Button
          startIcon={<NavigateBefore />}
          onClick={() => navigate(`/modules/${moduleSlug}`)}
          sx={{ mb: 2 }}
        >
          Back to Module
        </Button>
        <Typography variant="h4" gutterBottom>
          {lesson.title}
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Chip label={`${lesson.estimated_minutes} min`} size="small" />
          <Chip label={`${lesson.xp_reward} XP`} color="primary" size="small" />
          {lesson.exercise_count > 0 && (
            <Chip label={`${lesson.exercise_count} exercises`} size="small" />
          )}
        </Box>
      </Box>

      {completed && (
        <Alert severity="success" icon={<CheckCircle />} sx={{ mb: 3 }}>
          Lesson completed! You earned {lesson.xp_reward} XP. 🎉
        </Alert>
      )}

      {/* Lesson Content */}
      <Box sx={{ mb: 4 }}>
        <MarkdownViewer content={lesson.content} />
      </Box>

      {/* Resources */}
      {lesson.resources && lesson.resources.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Additional Resources
          </Typography>
          <Grid container spacing={2}>
            {lesson.resources.map((resource) => (
              <Grid item xs={12} sm={6} md={4} key={resource.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      {resource.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {resource.description}
                    </Typography>
                    <Button
                      size="small"
                      href={resource.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Open Resource
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Exercises */}
      {exercises.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Practice Exercises
          </Typography>
          <Grid container spacing={2}>
            {exercises.map((exercise) => (
              <Grid item xs={12} sm={6} key={exercise.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Typography variant="h6">{exercise.title}</Typography>
                      {exercise.user_passed && <CheckCircle color="success" />}
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {exercise.description.substring(0, 100)}...
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                      <Chip label={exercise.difficulty} size="small" />
                      <Chip label={`${exercise.xp_reward} XP`} color="primary" size="small" />
                      {exercise.user_attempts > 0 && (
                        <Chip
                          label={`${exercise.user_attempts} attempts`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Box>
                    <Button
                      fullWidth
                      variant="contained"
                      onClick={() => handleStartExercise(exercise.id)}
                    >
                      {exercise.user_passed ? 'Practice Again' : 'Start Exercise'}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Complete Lesson Button */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<CheckCircle />}
          onClick={handleComplete}
          disabled={markCompleteMutation.isLoading || completed}
        >
          {completed ? 'Lesson Completed!' : 'Mark as Complete'}
        </Button>
      </Box>
    </Box>
  )
}

export default LessonView
