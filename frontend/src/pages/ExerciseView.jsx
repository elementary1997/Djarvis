import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from 'react-query'
import {
  Box,
  Typography,
  Button,
  Grid,
  Paper,
  Alert,
  Chip,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material'
import {
  PlayArrow,
  NavigateBefore,
  CheckCircle,
  Error,
  ExpandMore,
  Lightbulb,
} from '@mui/icons-material'
import { exercisesAPI, sandboxAPI } from '../services/api'
import CodeEditor from '../components/CodeEditor'
import MarkdownViewer from '../components/MarkdownViewer'

const ExerciseView = () => {
  const { exerciseId } = useParams()
  const navigate = useNavigate()
  const [code, setCode] = useState('')
  const [output, setOutput] = useState(null)
  const [hintsRevealed, setHintsRevealed] = useState(0)

  const { data: exerciseData, isLoading } = useQuery(
    ['exercise', exerciseId],
    () => exercisesAPI.getExercise(exerciseId),
    {
      onSuccess: (data) => {
        setCode(data.data.starter_code || '')
      },
    }
  )

  const executeMutation = useMutation(
    (codeToExecute) =>
      sandboxAPI.executeCode({ code: codeToExecute, exercise_id: exerciseId }),
    {
      onSuccess: (data) => {
        setOutput(data.data)
      },
    }
  )

  const handleRevealHint = () => {
    if (hintsRevealed < exercise.hints.length) {
      setHintsRevealed(hintsRevealed + 1)
    }
  }

  const handleRunCode = () => {
    executeMutation.mutate(code)
  }

  if (isLoading) {
    return <CircularProgress />
  }

  const exercise = exerciseData?.data

  return (
    <Box>
      <Button
        startIcon={<NavigateBefore />}
        onClick={() => navigate(-1)}
        sx={{ mb: 2 }}
      >
        Back
      </Button>

      <Typography variant="h4" gutterBottom>
        {exercise.title}
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Chip label={exercise.difficulty} color="primary" />
        <Chip label={`${exercise.xp_reward} XP`} color="success" />
        {exercise.max_attempts > 0 && (
          <Chip
            label={`${exercise.user_attempts}/${exercise.max_attempts} attempts`}
            variant="outlined"
          />
        )}
      </Box>

      <Grid container spacing={3}>
        {/* Instructions */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Task Description
            </Typography>
            <MarkdownViewer content={exercise.description} />
          </Paper>

          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Instructions
            </Typography>
            <MarkdownViewer content={exercise.instructions} />
          </Paper>

          {/* Hints */}
          {exercise.hints && exercise.hints.length > 0 && (
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Lightbulb sx={{ mr: 1, color: 'warning.main' }} />
                <Typography variant="h6">Hints</Typography>
              </Box>
              {exercise.hints.slice(0, hintsRevealed).map((hint, index) => (
                <Alert key={index} severity="info" sx={{ mb: 1 }}>
                  <Typography variant="body2">{hint}</Typography>
                </Alert>
              ))}
              {hintsRevealed < exercise.hints.length && (
                <Button
                  variant="outlined"
                  size="small"
                  onClick={handleRevealHint}
                  startIcon={<Lightbulb />}
                >
                  Reveal Hint ({hintsRevealed + 1}/{exercise.hints.length})
                </Button>
              )}
            </Paper>
          )}
        </Grid>

        {/* Code Editor & Output */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Your Ansible Playbook
            </Typography>
            <CodeEditor value={code} onChange={setCode} height="400px" />
            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={
                  executeMutation.isLoading ? <CircularProgress size={20} /> : <PlayArrow />
                }
                onClick={handleRunCode}
                disabled={executeMutation.isLoading}
              >
                {executeMutation.isLoading ? 'Executing...' : 'Run Code'}
              </Button>
            </Box>
          </Paper>

          {/* Output */}
          {output && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Results
              </Typography>

              {output.is_passed ? (
                <Alert severity="success" icon={<CheckCircle />} sx={{ mb: 2 }}>
                  <Typography variant="h6">Exercise Passed! 🎉</Typography>
                  <Typography variant="body2">
                    You earned {exercise.xp_reward} XP!
                  </Typography>
                </Alert>
              ) : (
                <Alert severity="error" icon={<Error />} sx={{ mb: 2 }}>
                  <Typography variant="h6">Exercise Failed</Typography>
                  <Typography variant="body2">
                    Keep trying! Review the hints and test results.
                  </Typography>
                </Alert>
              )}

              {/* Test Results */}
              {output.test_results && (
                <Accordion defaultExpanded>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>Test Results</Typography>
                    <Chip
                      label={`${output.test_results.passed_tests}/${output.test_results.total_tests} passed`}
                      color={output.test_results.passed ? 'success' : 'error'}
                      size="small"
                      sx={{ ml: 2 }}
                    />
                  </AccordionSummary>
                  <AccordionDetails>
                    <List dense>
                      {output.test_results.test_results?.map((test, index) => (
                        <React.Fragment key={index}>
                          <ListItem>
                            {test.passed ? (
                              <CheckCircle color="success" sx={{ mr: 1 }} />
                            ) : (
                              <Error color="error" sx={{ mr: 1 }} />
                            )}
                            <ListItemText
                              primary={test.name}
                              secondary={test.error || test.message}
                            />
                          </ListItem>
                          {index < output.test_results.test_results.length - 1 && <Divider />}
                        </React.Fragment>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Console Output */}
              {output.stdout && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>Console Output</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box
                      component="pre"
                      sx={{
                        p: 2,
                        bgcolor: 'grey.900',
                        color: 'grey.100',
                        borderRadius: 1,
                        overflow: 'auto',
                        fontSize: '0.875rem',
                      }}
                    >
                      {output.stdout}
                    </Box>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Errors */}
              {output.stderr && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography color="error">Errors</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box
                      component="pre"
                      sx={{
                        p: 2,
                        bgcolor: 'error.dark',
                        color: 'white',
                        borderRadius: 1,
                        overflow: 'auto',
                        fontSize: '0.875rem',
                      }}
                    >
                      {output.stderr}
                    </Box>
                  </AccordionDetails>
                </Accordion>
              )}

              <Typography variant="caption" color="text.secondary" sx={{ mt: 2 }}>
                Execution time: {output.execution_time?.toFixed(2)}s
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  )
}

export default ExerciseView
