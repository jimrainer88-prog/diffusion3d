"""
Mesh utilities for checking 3D models
"""
import trimesh
from pathlib import Path


def get_vertices(mesh_path):
    """Return the number of vertices in a mesh."""
    mesh = trimesh.load(mesh_path, force='mesh')
    return len(mesh.vertices)


def get_faces(mesh_path):
    """Return the number of faces in a mesh."""
    mesh = trimesh.load(mesh_path, force='mesh')
    return len(mesh.faces)


def has_colors(mesh_path):
    """True only if the mesh really stores vertex/face colors or a texture.
    (trimesh fills a default gray vertex_colors array even when there are none.)"""
    mesh = trimesh.load(mesh_path, force='mesh')
    return mesh.visual.kind in ("vertex", "face", "texture")


def is_watertight(mesh_path):
    """Check if mesh is watertight (no holes)."""
    mesh = trimesh.load(mesh_path, force='mesh')
    return mesh.is_watertight


def get_bounding_box_size(mesh_path):
    """Return the size of the mesh's bounding box."""
    mesh = trimesh.load(mesh_path, force='mesh')
    bounding_box = mesh.extents
    return tuple(bounding_box)


def check_mesh(mesh_path):
    """Perform all checks on a mesh and return results."""
    if not Path(mesh_path).exists():
        raise FileNotFoundError(f"Mesh file not found: {mesh_path}")
    
    stats = {
        'vertices': get_vertices(mesh_path),
        'faces': get_faces(mesh_path),
        'has_colors': has_colors(mesh_path),
        'open_edges_pieces': hole_stats(mesh_path),
        'watertight': is_watertight(mesh_path),
        'bounding_box_size': get_bounding_box_size(mesh_path)
    }
    return stats


def hole_stats(mesh_path):
    """(open_edges, pieces): edges used by only one face = hole borders; separate connected parts."""
    import numpy as np
    mesh = trimesh.load(mesh_path, force='mesh')
    _, counts = np.unique(mesh.edges_sorted, axis=0, return_counts=True)
    open_edges = int((counts == 1).sum())
    pieces = len(mesh.split(only_watertight=False))
    return open_edges, pieces
