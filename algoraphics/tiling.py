"""
tiling.py
=========
Fill a region or the canvas with tiles or webs.

"""

import math
import numpy as np
from scipy import spatial
from typing import Union, Tuple, List, Sequence

from .main import add_margin, bounding_box, region_background
from .shapes import (
    rotated_bounding_box,
    rotate_shapes,
    keep_shapes_inside,
    polygon,
    line,
    set_style,
)
from .geom import midpoint, spaced_points
from .color import Color

Number = Union[int, float]
Point = Tuple[Number, Number]
Bounds = Tuple[Number, Number, Number, Number]
Collection = Union[list, dict]


def voronoi_regions(points: Sequence[Point]) -> List[dict]:
    """Find Voronoi regions for a set of points.

    Args:
        points: A list of points.

    Returns:
        A list of polygon shapes.  Items do not correspond to input
        points because points on the periphery do not have finite
        regions.

    """
    vor = spatial.Voronoi(np.array(points))
    regions = [
        [tuple(vor.vertices[i]) for i in region]
        for region in vor.regions
        if -1 not in region and len(region) > 0
    ]
    polygons = [polygon(points=region) for region in regions]
    set_style(polygons, "stroke", "match")
    set_style(polygons, "stroke-width", 0.3)
    return polygons


def voronoi_edges(points: Sequence[Point]) -> List[dict]:
    """Find the edges of Voronoi regions for a set of points.

    Args:
        points: A list of points.

    Returns:
        A list of line shapes.

    """
    vor = spatial.Voronoi(np.array(points))
    edges = [
        [tuple(vor.vertices[i]) for i in edge]
        for edge in vor.ridge_vertices
        if -1 not in edge
    ]
    return [line(p1=edge[0], p2=edge[1]) for edge in edges]


def delaunay_regions(points: Sequence[Point]) -> List[dict]:
    """Find the Delaunay regions for a set of points.

    Args:
        points: A list of points.

    Returns:
        A list of triangular polygon shapes.  Items do not correspond
        to input points because points on the periphery do not have
        finite regions.

    """

    tri = spatial.Delaunay(np.array(points))
    regions = [[points[i] for i in region] for region in tri.simplices]
    polygons = [polygon(points=region) for region in regions]
    set_style(polygons, "stroke", "match")
    set_style(polygons, "stroke-width", 1)
    return polygons


def delaunay_edges(points: Sequence[Point]) -> List[dict]:
    """Find edges of Delaunay regions for a set of points.

    Args:
        points: A list of points.

    Returns:
        A list of line shapes.

    """
    tri = spatial.Delaunay(np.array(points))
    edges = []
    for simplex in tri.simplices:
        simplex = list(simplex) + [simplex[0]]
        for i in range(len(simplex) - 1):
            edge = [simplex[i], simplex[i + 1]]
            edge.sort()  # so unique edges can be identified
            edges.append(edge)
    edges = [list(x) for x in set(tuple(x) for x in edges)]  # unique edges
    edges = [[tuple(tri.points[i]) for i in ed] for ed in edges]
    return [line(p1=ed[0], p2=ed[1]) for ed in edges]


def tile_region(
    outline: Collection,
    shape: str = "polygon",
    edges: bool = False,
    tile_size: Number = 500,
    regularity: int = 10,
) -> dict:
    """Fill region with (uncolored) tiles or tile edges.

    Args:
        outline: The shape/s that will become the clip.
        shape: Either 'polygon' for Voronoi tiling or 'triangle' for
          Delaunay tiling.
        edges: Whether to return the edges around tiles as lines
          instead of the tiles themselves.
        tile_size: The approximate area of each tile.
        regularity: A value of one or higher, passed to ``spaced_points()``.

    Returns:
        A group with clip.

    """
    bounds = add_margin(bounding_box(outline), 30)
    w = bounds[2] - bounds[0]
    h = bounds[3] - bounds[1]
    n_points = int(float(w * h) / tile_size)
    points = spaced_points(n_points, bounds, regularity)
    if shape == "polygon" and not edges:
        tiles = voronoi_regions(points)
    elif shape == "polygon" and edges:
        tiles = voronoi_edges(points)
    elif shape == "triangle" and not edges:
        tiles = delaunay_regions(points)
    elif shape == "triangle" and edges:
        tiles = delaunay_edges(points)
    else:
        raise ValueError("Invalid tile specification.")
    return dict(type="group", clip=outline, members=tiles)


def tile_canvas(
    w: Number,
    h: Number,
    shape: str = "polygon",
    edges: bool = False,
    tile_size: Number = 500,
    regularity: int = 10,
) -> List[dict]:
    """Fill canvas with (uncolored) tiles.

    Args:
        w: Width of the canvas.
        h: Height of the canvas.
        tile_shape: Either 'polygon' for Voronoi tiling or 'triangle'
          for Delaunay tiling.
        edges: Whether to return the edges around tiles as lines
          instead of the tiles themselves.
        tile_size: The approximate area of each tile.
        regularity: A value of one or higher, passed to ``spaced_points``.

    Returns:
        A list of polygon or line shapes.

    """
    margin = 30
    bounds = add_margin((0, 0, w, h), margin)
    w = bounds[2] - bounds[0]
    h = bounds[3] - bounds[1]
    n_points = int(float(w * h) / tile_size)
    points = spaced_points(n_points, bounds, regularity)
    if shape == "polygon" and not edges:
        tiles = voronoi_regions(points)
    elif shape == "polygon" and edges:
        tiles = voronoi_edges(points)
    elif shape == "triangle" and not edges:
        tiles = delaunay_regions(points)
    elif shape == "triangle" and edges:
        tiles = delaunay_edges(points)
    else:
        raise ValueError("Invalid tile specification.")
    return tiles


def nested_triangles(
    tip: Point, height: Number, min_level: int, max_level: int
) -> List[dict]:
    """Generate nested equilateral triangles.

    Args:
        tip: The tip of the bounding triangle.
        height: The height of the bounding triangle (negative for
          upside-down triangle).
        min_level: The level of the largest triangles (0 is the
          bounding triangle).
        max_level: The level of the smallest triangles.

    Returns:
        A list of triangle polygon shapes.

    """

    def process_triangle(tip, height, level, triangles):
        b1 = (tip[0] - height / math.sqrt(3), tip[1] - height)
        b2 = (tip[0] + height / math.sqrt(3), tip[1] - height)
        if (level < min_level) or (level < max_level and np.random.random() < 0.75):
            process_triangle(tip, height / 2, level + 1, triangles)
            process_triangle(midpoint(tip, b1), height / 2, level + 1, triangles)
            process_triangle(midpoint(tip, b2), height / 2, level + 1, triangles)
            process_triangle(
                (tip[0], tip[1] - height), -height / 2, level + 1, triangles
            )
        elif height > 0:  # only draw upward-pointing triangles
            triangles.append(polygon(points=[tip, b1, b2]))

    triangles = []
    process_triangle(tip, height, 0, triangles)
    return triangles


def fill_nested_triangles(
    outline: Collection,
    min_level: int,
    max_level: int,
    color: Color = None,
    color2: Color = None,
) -> dict:
    """Fill region with nested triangle pattern.

    Args:
        outline: A region outline shape or collection.
        min_level: The level of the largest triangles (0 is bounding triangle).
        max_level: The level of the smallest triangles.
        color1: The color/s for half of the triangles.
        color2: The color for the opposing half of the triangles.
          This half of triangles will all be one color because it is
          the background.

    Returns:
        A group with the outline as clip.

    """
    rotation = np.random.uniform(0, 360)
    bounds = add_margin(rotated_bounding_box(outline, rotation), 10)
    w = bounds[2] - bounds[0]
    tip = (bounds[0] + w / 2, bounds[3] + (w / 2) * math.sqrt(3))
    height = tip[1] - bounds[1]
    triangles = nested_triangles(tip, height, min_level, max_level)
    rotate_shapes(triangles, rotation)
    keep_shapes_inside(triangles, outline)
    region = dict(type="group", clip=outline, members=triangles)
    if color is not None:
        set_style(region["members"], "fill", color)
    if color2 is not None:
        region_background(region, color2)
    return region
