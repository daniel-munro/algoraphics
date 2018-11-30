"""
tiling.py
=========
Fill a region or the canvas with tiles or webs.

"""

import math
import numpy as np
from scipy import spatial

from .main import set_style, add_margin, bounding_box, region_background
from .shapes import rotated_bounding_box, rotate_shapes, keep_shapes_inside
from .shapes import polygon
from .geom import Rtree, distance, midpoint


def spaced_points(n, n_cand, bounds):
    """Generate random but evenly-spaced points.

    Uses Mitchell's best-candidate algorithm.

    Args:
        n (int): Number of points to generate.
        n_cand (int): Number of candidate points to generate for each output point.  Higher numbers result in higher regularity.
        bounds (tuple): A bounds tuple.

    Returns:
        list: The generated points.

    """
    x_min, x_max, y_min, y_max = bounds
    points = [(np.random.uniform(x_min, x_max),
               np.random.uniform(y_min, y_max))]
    idx = Rtree(points)

    for i in range(1, n):
        best_distance = 0
        for j in range(n_cand):
            cand = (np.random.uniform(x_min, x_max),
                    np.random.uniform(y_min, y_max))
            nearest = idx.nearest(cand)
            dist = distance(nearest, cand)
            if dist > best_distance:
                best_distance = dist
                best_candidate = cand
        points.append(best_candidate)
        idx.add_point(best_candidate)
    return points


# this version always returns list with elements corresponding to input points (i.e. returns None for point with no region), but I don't think this is useful.
# def voronoi_regions(points):
#     vor = spatial.Voronoi(np.array(points))
#     regions = [[tuple(vor.vertices[i]) for i in region] if -1 not in region else None for region in vor.regions]
#     return [regions[i] if i != -1 else None for i in vor.point_region]

def voronoi_regions(points):
    """Find Voronoi regions for a set of points.

    Args:
        points (list): A list of points.

    Returns:
        list: A list of polygon shapes.  Items do not correspond to
        input points because points on the periphery do not have
        finite regions.

    """
    vor = spatial.Voronoi(np.array(points))
    regions = [[tuple(vor.vertices[i]) for i in region] for region in
               vor.regions if -1 not in region and len(region) > 0]
    polygons = [polygon(points=region) for region in regions]
    set_style(polygons, 'stroke', 'match')
    set_style(polygons, 'stroke-width', 0.3)
    return polygons


def voronoi_edges(points):
    """Find the edges of Voronoi regions for a set of points.

    Args:
        points (list): A list of points.

    Returns:
        list: A list of line shapes.

    """
    vor = spatial.Voronoi(np.array(points))
    edges = [[tuple(vor.vertices[i]) for i in edge] for edge in
             vor.ridge_vertices if -1 not in edge]
    return [dict(type='line', p1=edge[0], p2=edge[1]) for edge in edges]


def delaunay_regions(points):
    """Find the Delaunay regions for a set of points.

    Args:
        points (list): A list of points.

    Returns:
        list: A list of triangular polygon shapes.  Items do not
        correspond to input points because points on the periphery do
        not have finite regions.

    """

    tri = spatial.Delaunay(np.array(points))
    regions = [[points[i] for i in region] for region in tri.simplices]
    polygons = [dict(type='polygon', points=region) for region in regions]
    set_style(polygons, 'stroke', 'match')
    set_style(polygons, 'stroke-width', 1)
    return polygons


def delaunay_edges(points):
    """Find edges of Delaunay regions for a set of points.

    Args:
        points (list): A list of points.

    Returns:
        list: A list of line shapes.

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
    return [dict(type='line', p1=ed[0], p2=ed[1]) for ed in edges]


def tile_region(outline, shape='polygon', edges=False, tile_size=500,
                regularity=10):
    """Fill region with (uncolored) tiles or tile edges.

    Args:
        outline (dict|list): The shape/s that will become the clip.
        shape (str): Either 'polygon' for Voronoi tiling or 'triangle' for Delaunay tiling.
        edges (bool): Whether to return the edges around tiles as lines instead of the tiles themselves.
        tile_size (float|int): The approximate area of each tile.
        regularity (int): A value of one or higher, passed to spaced_points.

    Returns:
        dict: A group with clip.

    """
    bounds = add_margin(bounding_box(outline), 30)
    w = bounds[1] - bounds[0]
    h = bounds[3] - bounds[2]
    n_points = int(float(w * h) / tile_size)
    points = spaced_points(n_points, regularity, bounds)
    if shape == 'polygon' and not edges:
        tiles = voronoi_regions(points)
    elif shape == 'polygon' and edges:
        tiles = voronoi_edges(points)
    elif shape == 'triangle' and not edges:
        tiles = delaunay_regions(points)
    elif shape == 'triangle' and edges:
        tiles = delaunay_edges(points)
    else:
        raise ValueError("Invalid tile specification.")
    return dict(type='group', clip=outline, members=tiles)


def tile_canvas(w, h, shape='polygon', edges=False, tile_size=500,
                regularity=10):
    """Fill canvas with (uncolored) tiles.

    Args:
        w (int): Width of the canvas.
        h (int): Height of the canvas.
        tile_shape (str): Either 'polygon' for Voronoi tiling or 'triangle' for Delaunay tiling.
        edges (bool): Whether to return the edges around tiles as lines instead of the tiles themselves.
        tile_size (float|int): The approximate area of each tile.
        regularity (int): A value of one or higher, passed to spaced_points.

    Returns:
        list: A list of shapes.

    """
    margin = 30
    bounds = add_margin((0, w, 0, h), margin)
    w = bounds[1] - bounds[0]
    h = bounds[3] - bounds[2]
    n_points = int(float(w * h) / tile_size)
    points = spaced_points(n_points, regularity, bounds)
    if shape == 'polygon' and not edges:
        tiles = voronoi_regions(points)
    elif shape == 'polygon' and edges:
        tiles = voronoi_edges(points)
    elif shape == 'triangle' and not edges:
        tiles = delaunay_regions(points)
    elif shape == 'triangle' and edges:
        tiles = delaunay_edges(points)
    else:
        raise ValueError("Invalid tile specification.")
    return tiles


def nested_triangles(tip, height, min_level, max_level):
    """Generate nested equilateral triangles.

    Args:
        tip (point): The tip of the bounding triangle.
        height (float|int): The height of the bounding triangle (negative for upside-down triangle).
        min_level (int): The level of the largest triangles (0 is the bounding triangle).
        max_level (int): The level of the smallest triangles.

    Returns:
        list: A list of triangle polygon shapes.

    """
    def process_triangle(tip, height, level, triangles):
        b1 = (tip[0] - height / math.sqrt(3), tip[1] - height)
        b2 = (tip[0] + height / math.sqrt(3), tip[1] - height)
        if ((level < min_level) or (level < max_level and
                                    np.random.random() < 0.75)):
            # tip1 = (tip[0] - height / 2. / math.sqrt(2), tip[1] - height / 2.)
            # tip2 = (tip[0] + height / 2. / math.sqrt(2), tip[1] - height / 2.)
            # tip3 = (tip[0], tip[1] - height)
            # for new_tip in [tip, tip1, tip2, tip3]:
            #     process_triangle(new_tip, height / 2., level - 1)
            process_triangle(tip, height / 2., level + 1, triangles)
            process_triangle(midpoint(tip, b1), height / 2.,
                             level + 1, triangles)
            process_triangle(midpoint(tip, b2), height / 2.,
                             level + 1, triangles)
            process_triangle((tip[0], tip[1] - height),
                             -height / 2., level + 1, triangles)
        elif height > 0:  # only draw upward-pointing triangles
            triangles.append(dict(type='polygon', points=[tip, b1, b2]))

    triangles = []
    process_triangle(tip, height, 0, triangles)
    return triangles


def fill_nested_triangles(outline, min_level, max_level, color=None,
                          color2=None):
    """Fill region with nested triangle pattern.

    Args:
        outline (dict|list): A region outline shape.
        min_level (int): The level of the largest triangles (0 is bounding triangle).
        max_level (int): The level of the smallest triangles.
        color1 (Color): The color/s for half of the triangles.
        color2 (Color): The color for the opposing half of the triangles.  This half of triangles will all be one color because it is the background.

    Returns:
        dict: A group with the outline as clip.

    """
    rotation = np.random.uniform(0, 360)
    bounds = add_margin(rotated_bounding_box(outline, rotation), 10)
    w = bounds[1] - bounds[0]
    tip = (bounds[0] + w / 2., bounds[3] + (w / 2.) * math.sqrt(3))
    height = tip[1] - bounds[2]
    triangles = nested_triangles(tip, height, min_level, max_level)
    rotate_shapes(triangles, rotation)
    keep_shapes_inside(triangles, outline)
    region = dict(type='group', clip=outline, members=triangles)
    if color is not None:
        set_style(region['members'], 'fill', color)
    if color2 is not None:
        region_background(region, color2)
    return region
