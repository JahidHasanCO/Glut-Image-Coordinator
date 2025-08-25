# Layer Window Feature - User Guide

The Layer window feature provides organized management of all objects on the canvas, allowing users to easily track, select, and manage images and drawings.

## Accessing the Layer Window

1. **Open Layer Window**: Go to `Layers` → `Show Layers` in the menu bar
2. The Layer window will open showing all current layers in a scrollable list

## Layer Types

### Image Layers
- **Created when**: You upload an image via `File` → `Open Image...`
- **Tag format**: `Image_filename.jpg` (uses actual filename)
- **Contains**: The canvas image object ID
- **Example**: `Image_background.jpg (1 objects)`

### Drawing Layers  
- **Created when**: You draw continuous strokes with the Pen tool
- **Tag format**: `drawing1`, `drawing2`, etc. (auto-numbered)
- **Contains**: All line segment IDs from that drawing session
- **Example**: `drawing1 (15 objects)` - contains 15 line segments

### Line Layers
- **Created when**: You use the Pen Point tool to draw individual line segments  
- **Tag format**: `line1`, `line2`, etc. (auto-numbered)
- **Contains**: Point IDs that make up the line (start point, end point, etc.)
- **Example**: `line1 (2 objects)` - contains start and end point IDs

## Layer Window Controls

### Layer List
- Shows all layers with their names and object counts
- Format: `LayerName (X objects) - Status`
- Status shows `Visible` or `Hidden`

### Buttons

#### **Refresh**
- Updates the layer list to show current state
- Useful after creating new drawings or images

#### **Hide Layer / Show Layer**  
- Toggles visibility of the selected layer
- Hidden layers remain in the list but objects are not visible on canvas
- Button text changes based on current state

#### **Delete Layer**
- Permanently removes the selected layer and all its objects from canvas
- Shows confirmation dialog before deletion
- Cannot be undone

## Using Layers

### Selecting Objects
1. **Click on any layer** in the list
2. **Objects highlight**: All objects in that layer get red outlines on the canvas
3. **Easy identification**: Quickly find and identify specific drawings or images

### Managing Visibility
1. **Select a layer** you want to hide/show
2. **Click Hide Layer** to make objects invisible (they remain on canvas)
3. **Click Show Layer** to make hidden objects visible again
4. **Useful for**: Temporarily removing visual clutter or focusing on specific elements

### Organizing Work
- **Images** get descriptive names based on filenames
- **Drawings** are grouped by drawing session (each pen stroke sequence)
- **Lines** are individual line segments for precise control

## Integration with Existing Tools

### Clear Draw Tool
- **Removes all drawing/line layers** when used
- **Preserves image layers** (images remain)
- **Layer list updates** automatically

### Canvas Operations
- **Automatic registration**: All new objects are automatically added to appropriate layers
- **Real-time updates**: Layer window reflects current canvas state
- **Error handling**: Gracefully handles deleted or modified objects

## Tips for Best Workflow

1. **Open Layer window early** in your session to track your work
2. **Use Hide/Show** to focus on specific elements while drawing
3. **Check object counts** to understand the complexity of your drawings  
4. **Select layers** to quickly identify objects when the canvas gets complex
5. **Use descriptive filenames** for images to make layer names more meaningful

## Technical Notes

- Layer window can be opened/closed multiple times safely
- Highlights are automatically removed when Layer window is closed
- Layer data persists as long as objects exist on canvas
- Multiple objects can be highlighted simultaneously by selecting different layers

This feature makes it easy to organize complex drawings with multiple images, shapes, and line work, exactly as requested in the original issue.