import { useState, useCallback } from 'react';

export function useBlocks() {
  const [blocks, setBlocks] = useState([]);
  const [undoStack, setUndoStack] = useState([]);
  const [redoStack, setRedoStack] = useState([]);

  const pushUndo = useCallback((blocks) => setUndoStack(stack => [...stack, blocks]), []);

  const addBlock = useCallback((block) => {
    pushUndo(blocks);
    setBlocks(b => [...b, block]);
  }, [blocks, pushUndo]);

  const editBlock = useCallback((id, newBlock) => {
    pushUndo(blocks);
    setBlocks(b => b.map(block => block.id === id ? { ...block, ...newBlock } : block));
  }, [blocks, pushUndo]);

  const deleteBlock = useCallback((id) => {
    pushUndo(blocks);
    setBlocks(b => b.filter(block => block.id !== id));
  }, [blocks, pushUndo]);

  const undo = useCallback(() => {
    if (undoStack.length === 0) return;
    setRedoStack(stack => [...stack, blocks]);
    setBlocks(undoStack[undoStack.length - 1]);
    setUndoStack(stack => stack.slice(0, -1));
  }, [undoStack, blocks]);

  const redo = useCallback(() => {
    if (redoStack.length === 0) return;
    setUndoStack(stack => [...stack, blocks]);
    setBlocks(redoStack[redoStack.length - 1]);
    setRedoStack(stack => stack.slice(0, -1));
  }, [redoStack, blocks]);

  return [blocks, setBlocks, addBlock, editBlock, deleteBlock, undo, redo];
} 