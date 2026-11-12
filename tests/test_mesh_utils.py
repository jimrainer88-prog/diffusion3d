"""
Tests for mesh utilities
"""
import os
import tempfile
import trimesh
import numpy as np

# Add project root to path so we can import our modules
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from utils.mesh_utils import get_vertices, get_faces, has_colors, is_watertight, get_bounding_box_size, check_mesh


def test_mesh_functions_with_synthetic_box():
    """Test mesh utility functions with a simple trimesh box."""
    # Create a simple box mesh using trimesh
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a simple box mesh
        box = trimesh.creation.box(extents=[1, 1, 1])
        
        # Save box to GLB file
        glb_path = os.path.join(tmpdir, "test_box.glb")
        box.export(glb_path)
        
        # Test all functions
        vertices_count = get_vertices(glb_path)
        faces_count = get_faces(glb_path)
        has_colors_result = has_colors(glb_path)
        watertight_result = is_watertight(glb_path)
        bbox_size = get_bounding_box_size(glb_path)
        
        # Basic checks
        assert vertices_count == 8, f"Expected 8 vertices, got {vertices_count}"
        assert faces_count == 12, f"Expected 12 faces, got {faces_count}"
        assert watertight_result is True, "Box should be watertight"
        assert has_colors_result is False, "Box should not have vertex colors by default"
        
        # Bounding box size should be around [1, 1, 1]
        assert len(bbox_size) == 3
        assert np.allclose(bbox_size, [1, 1, 1], atol=0.1)


def test_check_mesh_function():
    """Test the complete check_mesh function."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a simple box mesh
        box = trimesh.creation.box(extents=[2, 3, 4])
        
        # Save to GLB file
        glb_path = os.path.join(tmpdir, "test_box2.glb")
        box.export(glb_path)
        
        # Test check_mesh function
        stats = check_mesh(glb_path)
        
        # Verify all expected keys are present
        assert 'vertices' in stats
        assert 'faces' in stats
        assert 'has_colors' in stats
        assert 'watertight' in stats
        assert 'bounding_box_size' in stats
        
        # Verify values
        assert stats['vertices'] == 8
        assert stats['faces'] == 12
        assert stats['watertight'] is True
        assert not stats['has_colors']
        assert len(stats['bounding_box_size']) == 3
        assert np.allclose(stats['bounding_box_size'], [2, 3, 4], atol=0.1)


def test_nonexistent_mesh():
    """Test that check_mesh raises FileNotFoundError for nonexistent file."""
    try:
        check_mesh("/non/existent/file.glb")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass  # Expected