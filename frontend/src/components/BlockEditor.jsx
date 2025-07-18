import React, { useCallback } from 'react';
import NotionBlock from './NotionBlock';
import { v4 as uuidv4 } from 'uuid';
import { Button, Box } from '@mui/material';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';

const BlockEditor = ({ blocks, setBlocks, addBlock, editBlock, deleteBlock, undo, redo, externalAddTextBlock }) => {
  // Add block handlers (text, image, table, graph) can be implemented here or passed as props
  const handleAddText = useCallback(() => {
    addBlock({ id: uuidv4(), type: 'text', content: 'New text block' });
  }, [addBlock]);

  const handleDragEnd = (result) => {
    if (!result.destination) return;
    const reordered = Array.from(blocks);
    const [removed] = reordered.splice(result.source.index, 1);
    reordered.splice(result.destination.index, 0, removed);
    setBlocks(reordered);
  };

  React.useEffect(() => {
    if (externalAddTextBlock) {
      externalAddTextBlock((content) => addBlock({ id: uuidv4(), type: 'text', content }));
    }
  }, [externalAddTextBlock, addBlock]);

  return (
    <Box>
      <Button onClick={handleAddText} variant="outlined" sx={{ mb: 2, mr: 1 }}>Add Text Block</Button>
      <Button onClick={undo} variant="outlined" sx={{ ml: 1 }}>Undo</Button>
      <Button onClick={redo} variant="outlined" sx={{ ml: 1 }}>Redo</Button>
      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="notion-blocks">
          {(provided) => (
            <div ref={provided.innerRef} {...provided.droppableProps}>
              {blocks.map((block, idx) => (
                <Draggable key={block.id} draggableId={block.id} index={idx}>
                  {(provided) => (
                    <div ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps}>
                      <NotionBlock
                        block={block}
                        onEdit={editBlock}
                        onDelete={deleteBlock}
                      />
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>
    </Box>
  );
};

export default BlockEditor; 