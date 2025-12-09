import React from 'react'
import { useQuery } from 'react-query'
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Avatar,
  Chip,
  LinearProgress,
} from '@mui/material'
import { EmojiEvents } from '@mui/icons-material'
import { progressAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

const Leaderboard = () => {
  const { user } = useAuth()
  const { data, isLoading } = useQuery('leaderboard', progressAPI.getLeaderboard)

  if (isLoading) {
    return <LinearProgress />
  }

  const leaderboard = data?.data?.leaderboard || []
  const userRank = data?.data?.user_rank

  const getRankColor = (rank) => {
    if (rank === 1) return 'gold'
    if (rank === 2) return 'silver'
    if (rank === 3) return '#cd7f32' // bronze
    return 'grey.500'
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <EmojiEvents sx={{ fontSize: 40, mr: 2, color: 'warning.main' }} />
        <Box>
          <Typography variant="h4">Leaderboard</Typography>
          <Typography variant="body2" color="text.secondary">
            Top learners on Djarvis
          </Typography>
        </Box>
      </Box>

      {userRank && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: 'primary.light' }}>
          <Typography variant="h6" color="white">
            Your Rank: #{userRank}
          </Typography>
        </Paper>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell width={80}>
                <strong>Rank</strong>
              </TableCell>
              <TableCell>
                <strong>User</strong>
              </TableCell>
              <TableCell align="center">
                <strong>Level</strong>
              </TableCell>
              <TableCell align="center">
                <strong>Total XP</strong>
              </TableCell>
              <TableCell align="center">
                <strong>Exercises</strong>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {leaderboard.map((entry) => {
              const isCurrentUser = entry.user.id === user?.id
              return (
                <TableRow
                  key={entry.rank}
                  sx={{
                    bgcolor: isCurrentUser ? 'action.selected' : 'inherit',
                    '&:hover': { bgcolor: 'action.hover' },
                  }}
                >
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {entry.rank <= 3 && (
                        <EmojiEvents
                          sx={{ color: getRankColor(entry.rank), mr: 1 }}
                        />
                      )}
                      <Typography variant="h6">#{entry.rank}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar
                        src={entry.user.avatar}
                        sx={{ width: 40, height: 40 }}
                      >
                        {entry.user.username[0]?.toUpperCase()}
                      </Avatar>
                      <Box>
                        <Typography variant="body1">
                          {entry.user.username}
                          {isCurrentUser && (
                            <Chip label="You" size="small" color="primary" sx={{ ml: 1 }} />
                          )}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    <Chip label={`Level ${entry.user.level}`} color="primary" />
                  </TableCell>
                  <TableCell align="center">
                    <Typography variant="body1" fontWeight="bold">
                      {entry.user.total_xp.toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Typography variant="body1">
                      {entry.completed_exercises}
                    </Typography>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {leaderboard.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body1" color="text.secondary">
            No users on the leaderboard yet. Be the first!
          </Typography>
        </Box>
      )}
    </Box>
  )
}

export default Leaderboard
