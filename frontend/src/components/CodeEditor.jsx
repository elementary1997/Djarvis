import React, { useRef } from 'react'
import Editor from '@monaco-editor/react'
import { Box, Paper } from '@mui/material'

const CodeEditor = ({ value, onChange, height = '500px', language = 'yaml', readOnly = false }) => {
  const editorRef = useRef(null)

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor

    // Configure Ansible/YAML syntax highlighting
    monaco.languages.setMonarchTokensProvider('yaml', {
      tokenizer: {
        root: [
          [/^\s*-\s/, 'keyword'],
          [/^\s*[a-zA-Z_][a-zA-Z0-9_]*:/, 'type'],
          [/".*?"/, 'string'],
          [/'.*?'/, 'string'],
          [/#.*$/, 'comment'],
          [/\{\{.*?\}\}/, 'variable'],
        ],
      },
    })
  }

  const editorOptions = {
    minimap: { enabled: false },
    fontSize: 14,
    lineNumbers: 'on',
    scrollBeyondLastLine: false,
    automaticLayout: true,
    tabSize: 2,
    wordWrap: 'on',
    readOnly,
    theme: 'vs-dark',
  }

  return (
    <Paper elevation={2}>
      <Box sx={{ border: '1px solid #ddd', borderRadius: 1, overflow: 'hidden' }}>
        <Editor
          height={height}
          language={language}
          value={value}
          onChange={onChange}
          onMount={handleEditorDidMount}
          options={editorOptions}
        />
      </Box>
    </Paper>
  )
}

export default CodeEditor
