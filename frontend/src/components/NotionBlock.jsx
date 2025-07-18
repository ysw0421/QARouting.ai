import React, { useState } from 'react';
import { Typography, Paper, Table, TableBody, TableCell, TableHead, TableRow, IconButton, Box, TextField, Button } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';

const NotionBlock = ({ block, onEdit, onDelete }) => {
  const [editing, setEditing] = useState(false);
  const [editValue, setEditValue] = useState(block.content || '');

  return (
    <Paper sx={{ p: 2, mb: 2, position: 'relative' }}>
      <Box sx={{ position: 'absolute', top: 8, right: 8 }}>
        <IconButton size="small" onClick={() => setEditing(true)}><EditIcon fontSize="small" /></IconButton>
        <IconButton size="small" onClick={() => onDelete(block.id)}><DeleteIcon fontSize="small" /></IconButton>
      </Box>
      {editing && block.type === 'text' ? (
        <Box>
          <TextField
            value={editValue}
            onChange={e => setEditValue(e.target.value)}
            fullWidth
            size="small"
            multiline
          />
          <Button onClick={() => { onEdit(block.id, { content: editValue }); setEditing(false); }} variant="contained" size="small" sx={{ mt: 1, mr: 1 }}>Save</Button>
          <Button onClick={() => setEditing(false)} size="small" sx={{ mt: 1 }}>Cancel</Button>
        </Box>
      ) : (
        <>
          {block.type === 'text' && <Typography>{block.content}</Typography>}
          {block.type === 'image' && block.url && <img src={block.url} alt="block" style={{ maxWidth: '100%' }} />}
          {block.type === 'table' && Array.isArray(block.data) && Array.isArray((block.data)[0]) && (
            <Table size="small">
              <TableHead>
                <TableRow>
                  {(block.data)[0]?.map((_, i) => (
                    <TableCell key={i}>Col {i + 1}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {(block.data).map((row, i) => (
                  <TableRow key={i}>
                    {row.map((cell, j) => (
                      <TableCell key={j}>{cell}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {block.type === 'graph' && Array.isArray(block.data) && (block.data).map && (
            <>
              <Typography color="textSecondary">[Graph Placeholder]</Typography>
              <Typography variant="body2" color="textSecondary">(Input Data)</Typography>
              <ul style={{ margin: 0, paddingLeft: 16 }}>
                {(block.data).map((row, i) => (
                  <li key={i}>X: {row.x}, Y: {row.y}</li>
                ))}
              </ul>
            </>
          )}
        </>
      )}
    </Paper>
  );
};

export default NotionBlock; 