import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Box, Paper, Typography } from '@mui/material'
import { styled } from '@mui/material/styles'

const StyledMarkdown = styled(Box)(({ theme }) => ({
  '& h1': {
    ...theme.typography.h4,
    marginTop: theme.spacing(3),
    marginBottom: theme.spacing(2),
  },
  '& h2': {
    ...theme.typography.h5,
    marginTop: theme.spacing(2.5),
    marginBottom: theme.spacing(1.5),
  },
  '& h3': {
    ...theme.typography.h6,
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(1),
  },
  '& p': {
    ...theme.typography.body1,
    marginBottom: theme.spacing(2),
    lineHeight: 1.7,
  },
  '& ul, & ol': {
    marginBottom: theme.spacing(2),
    paddingLeft: theme.spacing(3),
  },
  '& li': {
    marginBottom: theme.spacing(1),
  },
  '& code': {
    backgroundColor: theme.palette.grey[100],
    padding: '2px 6px',
    borderRadius: 4,
    fontFamily: 'Consolas, Monaco, monospace',
    fontSize: '0.9em',
  },
  '& pre': {
    backgroundColor: theme.palette.grey[900],
    color: theme.palette.grey[100],
    padding: theme.spacing(2),
    borderRadius: theme.shape.borderRadius,
    overflow: 'auto',
    marginBottom: theme.spacing(2),
    '& code': {
      backgroundColor: 'transparent',
      padding: 0,
      color: 'inherit',
    },
  },
  '& blockquote': {
    borderLeft: `4px solid ${theme.palette.primary.main}`,
    paddingLeft: theme.spacing(2),
    marginLeft: 0,
    marginBottom: theme.spacing(2),
    color: theme.palette.text.secondary,
  },
  '& table': {
    borderCollapse: 'collapse',
    width: '100%',
    marginBottom: theme.spacing(2),
  },
  '& th, & td': {
    border: `1px solid ${theme.palette.divider}`,
    padding: theme.spacing(1),
    textAlign: 'left',
  },
  '& th': {
    backgroundColor: theme.palette.grey[100],
    fontWeight: 'bold',
  },
  '& a': {
    color: theme.palette.primary.main,
    textDecoration: 'none',
    '&:hover': {
      textDecoration: 'underline',
    },
  },
}))

const MarkdownViewer = ({ content }) => {
  return (
    <Paper elevation={1} sx={{ p: 3 }}>
      <StyledMarkdown>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      </StyledMarkdown>
    </Paper>
  )
}

export default MarkdownViewer
