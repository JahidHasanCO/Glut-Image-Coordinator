# Layer Window Visual Mockup

```
┌─────────────────────────────────┐
│ Layers                      ✕   │
├─────────────────────────────────┤
│                                 │
│  Canvas Layers                  │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ Image_background.jpg (1 o...│ │ ← Image layer
│ │ drawing1 (12 objects) - V...│ │ ← Pen drawing  
│ │ line1 (2 objects) - Visibl.│ │ ← Pen point line
│ │ Image_character.png (1 obj..│ │ ← Another image
│ │ drawing2 (8 objects) - Hid..│ │ ← Hidden drawing
│ │ shape1 (4 objects) - Visibl│ │ ← Shape/polygon
│ └─────────────────────────────┘ │
│                                 │
│ [Refresh] [Hide Layer] [Delete] │
│                                 │
└─────────────────────────────────┘
```

## Layer Selection Example

When user clicks on "drawing1 (12 objects)" in the layer list:

```
Main Canvas View:
┌────────────────────────────────────┐
│                                    │
│  🖼️ background.jpg                 │
│                                    │
│     ═══ Red highlighted lines ═══  │ ← Objects in drawing1
│     ═══ showing selection     ═══  │   get red outlines
│                                    │
│  📐 Other drawings (normal color)   │
│                                    │
└────────────────────────────────────┘
```

## Layer Types in Practice

```
Layer Type     │ Tag Example           │ Objects Contained
──────────────┼──────────────────────┼─────────────────────
Image         │ Image_logo.png       │ [canvas_img_001]
Drawing       │ drawing1             │ [line_001, line_002, 
              │                      │  line_003, ..., line_012]
Line          │ line1                │ [point_start_005, 
              │                      │  point_end_006]  
Shape         │ shape1               │ [point_001, point_002,
              │                      │  point_003, point_004]
```

This visual shows exactly how the Layer window integrates with the canvas to provide the functionality requested in the issue.