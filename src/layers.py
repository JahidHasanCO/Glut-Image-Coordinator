"""
Layer management classes for the Glut Image Coordinator application.
This module provides Layer and LayerManager classes for organizing canvas objects.
"""

class Layer:
    """Data class to store layer information with Tag/ID and List of Object IDs"""
    
    def __init__(self, tag, layer_type="drawing"):
        self.tag = tag  # Tag or ID like "Image1", "line1", etc.
        self.object_ids = []  # List of canvas object IDs
        self.layer_type = layer_type  # "image", "drawing", "line", "shape"
        self.visible = True
    
    def add_object_id(self, object_id):
        """Add an object ID to this layer"""
        if object_id not in self.object_ids:
            self.object_ids.append(object_id)
    
    def remove_object_id(self, object_id):
        """Remove an object ID from this layer"""
        if object_id in self.object_ids:
            self.object_ids.remove(object_id)
    
    def __str__(self):
        return f"{self.tag} ({len(self.object_ids)} objects)"


class LayerManager:
    """Manages all layers in the application"""
    
    def __init__(self):
        self.layers = []
        self.layer_counter = {"image": 0, "drawing": 0, "line": 0, "shape": 0}
    
    def create_layer(self, layer_type="drawing", custom_tag=None):
        """Create a new layer with auto-generated or custom tag"""
        if custom_tag:
            tag = custom_tag
        else:
            self.layer_counter[layer_type] += 1
            tag = f"{layer_type}{self.layer_counter[layer_type]}"
        
        layer = Layer(tag, layer_type)
        self.layers.append(layer)
        return layer
    
    def get_layer_by_tag(self, tag):
        """Get layer by its tag"""
        for layer in self.layers:
            if layer.tag == tag:
                return layer
        return None
    
    def remove_layer(self, tag):
        """Remove a layer by its tag"""
        self.layers = [layer for layer in self.layers if layer.tag != tag]
    
    def get_all_layers(self):
        """Get all layers"""
        return self.layers.copy()