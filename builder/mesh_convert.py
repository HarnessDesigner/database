"""STEP (.stp/.step) -> app mesh format conversion.

Ported from harness_designer/process/model_process.py (the OCP-based STEP
reader) and harness_designer/utils/mesh_normals.py (compute_normals, pure
numpy). Deliberately does NOT import harness_designer.utils as a package --
its __init__.py unconditionally imports ui_utils.py, which imports PySide6,
dragging a GUI toolkit into a headless CI script for no reason.

compute_aabb/compute_obb are reimplemented here as plain-numpy functions
replicating harness_designer/utils/bounding_boxes.py's math without its
geometry.point.Point wrapper (which pulls in a weakref-singleton metaclass
and app-wide callback machinery not needed for two bounding-box corners).

Mesh simplification (pyfqmr) is available via _reduce_triangles but is NOT
applied by default -- the app's own models3d table schema defaults `simplify`
to 0, so this builder matches that and ships full-resolution meshes unless
explicitly asked to simplify.
"""

import numpy as np
import pyfqmr
from OCP.TopAbs import TopAbs_REVERSED, TopAbs_FACE
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopLoc import TopLoc_Location
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS


class ModelLoadError(Exception):
    """Raised when a STEP file cannot be read/triangulated."""


def _ocp_read_shape(shape, lin_deflection=0.1, is_relative=False, ang_deflection=0.5):
    # Deliberately diverges from the original app's process/model_process.py
    # settings (theLinDeflection=0.001, isRelative=True, theAngDeflection=0.1)
    # -- isRelative=True scales the tolerance to each FACE's own size, and on
    # some real Bosch STP files (988KB on disk -- not a big/complex part) a
    # small-radius feature (fillet/thread/near-degenerate curve) triggered a
    # combinatorial explosion: 16-22 MILLION vertices out of a source file
    # the same size as ones that tessellate to ~500K. Absolute deflection
    # (isRelative=False) removes that per-face scaling; the coarser absolute
    # tolerance (0.1 vs the original 0.001) and angular tolerance (0.5 vs
    # 0.1 rad -- 0.5 is OCCT's own typical default) also meaningfully cut
    # triangle counts on the normal-sized models, not just the outliers.
    BRepMesh_IncrementalMesh(
        theShape=shape, theLinDeflection=lin_deflection,
        isRelative=is_relative, theAngDeflection=ang_deflection, isInParallel=True
    )

    vertices = []
    faces = []
    offset = 0

    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        loc = TopLoc_Location()
        poly_triangulation = BRep_Tool.Triangulation_s(
            TopoDS.Face_s(exp.Current()), loc)  # NOQA

        if not poly_triangulation:
            exp.Next()
            continue

        trsf = loc.Transformation()
        node_count = poly_triangulation.NbNodes()

        for i in range(1, node_count + 1):
            gp_pnt = poly_triangulation.Node(i).Transformed(trsf)
            vertices.append((gp_pnt.X(), gp_pnt.Y(), gp_pnt.Z()))

        facet_reversed = exp.Current().Orientation() == TopAbs_REVERSED
        order = [1, 3, 2] if facet_reversed else [1, 2, 3]

        for i in range(1, poly_triangulation.NbTriangles() + 1):
            tri = poly_triangulation.Triangle(i)
            faces.append([tri.Value(j) + offset - 1 for j in order])

        offset += node_count
        exp.Next()

    vertices = np.array(vertices, dtype=np.float32)
    faces = np.array(faces, dtype=np.int32)

    return vertices, faces


def _load_step(file: str, lin_deflection=0.1, is_relative=False,
               ang_deflection=0.5) -> tuple[np.ndarray, np.ndarray]:
    step_reader = STEPControl_Reader()
    step_reader.ReadFile(file)
    step_reader.TransferRoots()  # NOQA
    shape = step_reader.Shape()

    return _ocp_read_shape(shape, lin_deflection, is_relative, ang_deflection)


def _reduce_triangles(verts: np.ndarray, faces: np.ndarray, target_count: int,
                      aggressiveness: float, update_rate: int = 1,
                      max_iterations: int = 150) -> tuple[np.ndarray, np.ndarray]:
    mesh_simplifier = pyfqmr.Simplify()
    mesh_simplifier.setMesh(verts, faces)
    mesh_simplifier.simplify_mesh(
        target_count=target_count,
        update_rate=update_rate,
        max_iterations=max_iterations,
        aggressiveness=aggressiveness,
        lossless=False,
        verbose=False,
    )

    vertices, faces, _ = mesh_simplifier.getMesh()

    return vertices.reshape(-1, 3), faces.reshape(-1, 3)


def _center_model(vertices: np.ndarray) -> np.ndarray:
    """Recenter a mesh so the model's centroid sits at the origin.

    Manufacturer-supplied models don't always have (0, 0, 0) as their
    center -- alignment of objects in the app depends on them being
    consistently centered.
    """
    vertices_reshaped = vertices.reshape(-1, 3)
    centroid = vertices_reshaped.mean(axis=0)
    vertices_reshaped = vertices_reshaped - centroid
    return vertices_reshaped.reshape(-1, 3)


def _process_verts_for_normals(vertices: np.ndarray, faces: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    triangles = vertices[faces]

    v0 = triangles[:, 0, :]
    v1 = triangles[:, 1, :]
    v2 = triangles[:, 2, :]

    e1 = v1 - v0
    e2 = v2 - v0

    face_normals_raw = np.cross(e1, e2)  # NOQA

    norms = np.linalg.norm(face_normals_raw, axis=1, keepdims=True)
    safe = np.maximum(norms, 1e-6)
    face_normals = face_normals_raw / safe

    degenerate = (norms.squeeze() < 1e-6)
    if np.any(degenerate):
        face_normals[degenerate] = 0.0

    return triangles, face_normals


def compute_normals(vertices: np.ndarray, faces: np.ndarray) -> tuple[np.ndarray, int]:
    """Compute both smooth and face normals, packed with positions.

    :returns: (packed_array, vertex_count) -- packed_array is a flat
        float32 array of [positions | smooth normals | face normals],
        each block vertex_count*3 floats long.
    """
    triangles, face_normals = _process_verts_for_normals(vertices, faces)

    vertex_count_total = len(vertices)
    vertex_normal_sum = np.zeros((vertex_count_total, 3), dtype=float)

    repeated_face_normals = np.repeat(face_normals, 3, axis=0)
    vertex_indices = faces.ravel()
    np.add.at(vertex_normal_sum, vertex_indices, repeated_face_normals)

    vn_norm = np.linalg.norm(vertex_normal_sum, axis=1, keepdims=True)
    safe_vn_norm = np.maximum(vn_norm, 1e-6)
    smooth_normals = vertex_normal_sum / safe_vn_norm

    isolated = (vn_norm.squeeze() < 1e-6)
    if np.any(isolated):
        smooth_normals[isolated] = 0.0

    smooth_normals_array = smooth_normals[faces].astype(np.float32).ravel()

    normals = np.repeat(face_normals[:, np.newaxis, :], 3, axis=1)
    normals_array = normals.astype(np.float32).ravel()

    vertices_array = triangles.astype(np.float32).ravel()

    packed = np.concatenate((vertices_array, smooth_normals_array, normals_array))

    return packed, len(vertices_array) // 3


def compute_aabb(verts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Compute an axis-aligned bounding box from vertex positions.

    :returns: (min_corner, max_corner), each a (3,) float32 array.
    """
    return verts.min(axis=0), verts.max(axis=0)


def compute_obb(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
    """Construct the 8 bounding-box corner coordinates from two opposite corners."""
    x1, y1, z1 = p1
    x2, y2, z2 = p2

    return np.array([
        [x1, y1, z1],
        [x2, y1, z1],
        [x2, y2, z1],
        [x1, y2, z1],
        [x1, y1, z2],
        [x2, y1, z2],
        [x2, y2, z2],
        [x1, y2, z2],
    ], dtype=np.float32)


def convert_stp(stp_path: str, simplify: bool = False, target_count: int = 25000,
                aggressiveness: float = 5.0, lin_deflection: float = 0.1,
                is_relative: bool = False, ang_deflection: float = 0.5
                ) -> tuple[np.ndarray, int, list, list]:
    """Convert a STEP file to the app's packed mesh format.

    Full resolution by default (simplify=False), matching the app's own
    models3d schema default (`simplify` column defaults to 0). Pass
    simplify=True to reduce to target_count triangles via pyfqmr instead.

    lin_deflection/is_relative/ang_deflection control OCP's triangulation
    tolerance -- see _ocp_read_shape's docstring comment for why the
    defaults here are coarser and absolute (not relative) compared to the
    original app's settings.

    :returns: (packed_array, vertex_count, aabb, obb) -- aabb/obb are plain
        nested Python lists (JSON/str-serializable, matching how the app
        stores them as TEXT columns).
    """
    vertices, faces = _load_step(stp_path, lin_deflection, is_relative, ang_deflection)
    vertices = _center_model(vertices)

    if simplify and len(faces) > target_count:
        vertices, faces = _reduce_triangles(vertices, faces, target_count, aggressiveness)

    packed, vertex_count = compute_normals(vertices, faces)

    unpacked_verts = packed[:vertex_count * 3].reshape(-1, 3)
    p_min, p_max = compute_aabb(unpacked_verts)
    aabb = np.array([p_min, p_max], dtype=np.float32)
    aabb = [[float(str(item2)) for item2 in item1] for item1 in aabb.tolist()]

    obb = compute_obb(p_min, p_max)
    obb = [[float(str(item2)) for item2 in item1] for item1 in obb.tolist()]

    return packed, vertex_count, aabb, obb
