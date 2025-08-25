#!/usr/bin/env python3
"""
Demo script showing the layer functionality for the Glut Image Coordinator
This demonstrates how the layer system works as requested in the issue.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from layers import Layer, LayerManager

def demo_layer_functionality():
    """Demonstrate the layer functionality as described in the issue"""
    
    print("🎨 Glut Image Coordinator - Layer Window Feature Demo")
    print("=" * 60)
    
    # Initialize the layer manager
    manager = LayerManager()
    
    print("\n📷 1. Uploading an Image:")
    print("   User opens 'background.jpg'")
    
    # Simulate image upload
    image_layer = manager.create_layer("image", "Image_background.jpg")
    image_canvas_id = "canvas_img_001"  # Simulated canvas object ID
    image_layer.add_object_id(image_canvas_id)
    
    print(f"   ✓ Created layer: {image_layer}")
    print(f"   ✓ Canvas object ID: {image_canvas_id}")
    
    print("\n✏️  2. Drawing Lines/Shapes:")
    print("   User draws with pen tool...")
    
    # Simulate drawing a line
    line_layer = manager.create_layer("line", "line1")
    start_point = "canvas_line_start_002"
    end_point = "canvas_line_end_003"
    line_layer.add_object_id(start_point)
    line_layer.add_object_id(end_point)
    
    print(f"   ✓ Created layer: {line_layer}")
    print(f"   ✓ Line contains point IDs: {line_layer.object_ids}")
    
    # Simulate drawing a shape
    shape_layer = manager.create_layer("shape", "shape1")
    shape_points = ["canvas_point_004", "canvas_point_005", "canvas_point_006", "canvas_point_007"]
    for point in shape_points:
        shape_layer.add_object_id(point)
    
    print(f"   ✓ Created layer: {shape_layer}")
    print(f"   ✓ Shape contains point IDs: {shape_layer.object_ids}")
    
    print("\n📋 3. Layer Window Display:")
    print("   The Layer window would show a ListBox with:")
    
    all_layers = manager.get_all_layers()
    for i, layer in enumerate(all_layers, 1):
        print(f"   [{i}] {layer}")
    
    print("\n🎯 4. Layer Selection:")
    print("   User clicks on 'line1' in the Layer window...")
    
    selected_layer = manager.get_layer_by_tag("line1")
    if selected_layer:
        print(f"   ✓ Selected layer: {selected_layer}")
        print(f"   ✓ Highlighting objects with IDs: {selected_layer.object_ids}")
        print("   → Canvas would highlight the line by drawing red outlines around it")
    
    print("\n🔧 5. Layer Management:")
    print("   Available operations in Layer window:")
    print("   • Hide/Show layer (toggles visibility)")
    print("   • Delete layer (removes from canvas)")
    print("   • Refresh list")
    
    # Demonstrate hiding a layer
    shape_layer.visible = False
    print(f"\n   Hiding shape layer: {shape_layer.tag}")
    print("   → Canvas objects would be set to 'hidden' state")
    
    print("\n✨ Summary:")
    print("   ✓ Images get their own layers with descriptive names")
    print("   ✓ Lines and shapes store all their point IDs")
    print("   ✓ Layer window shows all layers in a ListBox")
    print("   ✓ Clicking layers highlights objects on canvas")
    print("   ✓ Layer visibility and deletion is supported")
    
    print("\n🎯 Issue Requirements Met:")
    print("   ✓ Data class stores Tag/ID and List of Object IDs")
    print("   ✓ Image layers: Tag='Image1' with image canvas ID")
    print("   ✓ Line/Shape layers: Tag='line1' with all point IDs")
    print("   ✓ ListBox display in Layer window")
    print("   ✓ Selection finds elements on canvas by IDs")

if __name__ == "__main__":
    demo_layer_functionality()