"""
geom.py
=======
General functions involving points in 2D space.

"""

import math
import random
import rtree


def rad(deg):
    """Convert degrees to radians."""
    return deg * 2 * math.pi / 360


def deg(rad):
    """Convert radians to degrees."""
    return rad / (2 * math.pi) * 360


def rand_point_on_circle(c, r):
    """Return random point on circle with center c and radius r."""
    theta = random.uniform(-math.pi, math.pi)
    return (c[0] + math.cos(theta) * r, c[1] + math.sin(theta) * r)


def points_on_line(start, end, spacing):
    """Generate points along a line.

    Args:
        start (point): The first point.
        end (point): The last point.
        spacing (float|int): The approximate (max) distance between adjacent points.

    Returns:
        A list of points.

    """
    n_points = math.ceil(distance(start, end) / spacing) + 1

    dx = float(end[0] - start[0]) / (n_points - 1)
    dy = float(end[1] - start[1]) / (n_points - 1)

    x = [start[0] + i * dx for i in range(n_points)]
    y = [start[1] + i * dy for i in range(n_points)]
    return list(zip(x, y))


def interpolate(points, spacing):
    """Insert interpolated points.

    Insert equally-spaced, linearly interpolated points into list such
    that consecutive points are no more than 'spacing' distance apart.

    Args:
        points (list): A list of points.
        spacing (float|int): Maximum distance between adjacent points.

    """
    for i in reversed(range(1, len(points))):
        if distance(points[i - 1], points[i]) > spacing:
            newpts = points_on_line(points[i - 1], points[i], spacing)[1:-1]
            points[i:i] = newpts


def points_on_arc(center, radius, theta_start, theta_end, spacing):
    """Generate points along an arc.

    Args:
        center (point): The center of the arc.
        radius (float|int): The radius of the arc.
        theta_start (float|int): The starting position in degrees.
        theta_end (float|int): The ending position in degrees.
        spacing (float|int): The approximate distance between adjacent points.

    Returns:
        A list of points.

    """
    theta_start = rad(theta_start)
    theta_end = rad(theta_end)
    theta = float(theta_end - theta_start)

    n_points = int(abs(theta) * radius / spacing) + 1

    theta_p = [theta_start + i * theta / (n_points - 1) for i in range(n_points)]
    return [endpoint(center, t, radius) for t in theta_p]


def endpoint(start, angle, distance):
    """Return a point some distance from a starting point in the direction (in radians) of angle."""
    x = start[0] + math.cos(angle) * distance
    y = start[1] + math.sin(angle) * distance
    return (x, y)


def move_toward(start, target, distance):
    """Return a point some distance from a starting point in the direction of a target
point."""
    angle = math.atan2(target[1] - start[1], target[0] - start[0])
    return endpoint(start, angle, distance)


def rotate_and_move(start, ref, angle, distance):
    """Get a point some distance from a starting point in a direction relative to another point.

    Combines rotated_point and move_toward.

    """
    x = rotated_point(ref, start, angle)
    return move_toward(start, x, distance)


def distance(p1, p2):
    """Return the distance between two points."""
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.sqrt(dx * dx + dy * dy)


def get_nearest(points, point, index=False):
    """Find the nearest point in a list to a target point.

    Args:
        points (list): A list of points.
        point (point): The target point.
        index (bool): Whether to return the point or its index in the list.

    Returns:
        If index is False, returns point, otherwise returns index of
        point in list.

    """
    nearest = 0
    nearest_dist = distance(points[nearest], point)
    for p in range(1, len(points)):
        dist = distance(points[p], point)
        if dist < nearest_dist:
            nearest = p
            nearest_dist = dist
    return nearest if index else points[nearest]


class Rtree:
    """TODO"""
    def __init__(self, points=None):
        if points is None:
            points = []
        self.idx = rtree.index.Index()
        self.points = []  # for retrieving points, e.g. last N
        self.size = 0
        for p in points:
            self.add_point(p)

    def add_point(self, point):
        self.idx.add(self.size, point)
        self.points.append(point)
        self.size += 1

    def add_points(self, points):
        for point in points:
            self.add_point(point)

    def nearest(self, point, n=1, index=False):
        a = list(self.idx.nearest(point, n))
        if not index:
            a = [self.points[x] for x in a]
        if n == 1:
            a = a[0]
        return a


def midpoint(p1, p2):
    """Return the midpoint between two points."""
    return (p1[0] + p2[0]) / 2., (p1[1] + p2[1]) / 2.


def angle_between(p1, p2, p3):
    """Return the angle (in radians) between segment p2->p1 and p2->p3.

    The angle can be negative.

    """
    dir1 = math.atan2(p1[1] - p2[1], p1[0] - p2[0])
    dir2 = math.atan2(p3[1] - p2[1], p3[0] - p2[0])
    return dir2 - dir1


def translated_point(point, dx, dy):
    """Return the point resulting from translating `point` by `dx` and `dy`.

    """
    return (point[0] + dx, point[1] + dy)


def rotated_point(point, pivot, angle):
    """Return the point resulting from rotating `point` around `pivot` point by `angle` (in radians).

    """
    x = ((point[0] - pivot[0]) * math.cos(angle))
    - ((point[1] - pivot[1]) * math.sin(angle))
    + pivot[0]
    y = ((point[1] - pivot[1]) * math.cos(angle))
    + ((point[0] - pivot[0]) * math.sin(angle))
    + pivot[1]
    return (x, y)


def scaled_point(point, cx, cy=None):
    """Return the new location of `point` after scaling coordinates.

    Provide either one scaling factor or cx and cy.

    """
    cy = cx if cy is None else cy
    return (point[0] * cx, point[1] * cy)


def in_box(point, x_min, x_max, y_min, y_max):
    """Determine if a point lies within the specified bounds."""
    in_bounds = (x_min < point[0] and point[0] < x_max and
                 y_min < point[1] and point[1] < y_max)
    return in_bounds


def in_ellipse(point, x_min, x_max, y_min, y_max):
    """Determine if a point lies within an ellipse with the specified bounds."""
    c = (x_min + x_max) / 2., (y_min + y_max) / 2.
    r_x = c[0] - x_min
    r_y = c[1] - y_min
    return ((point[0] - c[0]) / r_x) ** 2 + ((point[1] - c[1]) / r_y) ** 2 < 1


def horizontal_range(points):
    """Return the magnitude of the horizontal range of a list of points."""
    if len(points) == 0:
        return 0
    else:
        return max([x[0] for x in points]) - min([x[0] for x in points])


def translate_points(points, dx, dy):
    """Shift the location of points.

    Args:
        points (list): A list of points, which can be nested.
        dx (float): movement in x direction.
        dy (float): movement in y direction.

    """
    for i in range(len(points)):
        if isinstance(points[i], list):
            translate_points(points[i], dx, dy)
        else:
            points[i] = translated_point(points[i], dx, dy)


def scale_points(points, cx, cy=None):
    """Scale the coordinates of points.

    Args:
        points (list): A list of points, which can be nested.
        cx (float|int): The horizontal scale factor.
        cy (float|int): The vertical scale factor. If omitted, y-coordinates will be scaled by cx.

    """
    for i in range(len(points)):
        if isinstance(points[i], list):
            scale_points(points[i], cx, cy)
        else:
            points[i] = scaled_point(points[i], cx, cy)


def jitter_points(points, deviation, type):
    """Add noise to the locations of points.

    Args:
        points (list): A list of points.
        deviation (float|int): For gaussian jitter, the standard deviation. For uniform jitter, the maximum distance.
        type (str): The type of noise, 'gaussian' or 'uniform'.

    """
    for i in range(len(points)):
        angle = random.uniform(0, 2 * math.pi)
        if type == 'gaussian':
            dist = random.gauss(0, deviation)
        elif type == 'uniform':
            dist = random.uniform(0, deviation)
        points[i] = endpoint(points[i], angle, dist)


def jittered_points(points, deviation, type):
    """Like jitter_points but returns jittered points, not affecting the original list."""
    x = points[:]
    jitter_points(x, deviation, type)
    return x


def line_to_polygon(points, width):
    """Convert a sequence of points to a path outline.

    Imagining the points were connected with a stroke with positive
    width, the outline of the stroke is returned.

    Args:
        points (list): A list of line points.
        width (float): Width of the path to be outlined.

    Returns:
        A list of points.

    """

    pts = []
    end1 = rotate_and_move(points[0], points[1], -math.pi / 2, width / 2.)
    end2 = rotate_and_move(points[-1], points[-2], math.pi / 2, width / 2.)
    end3 = rotate_and_move(points[-1], points[-2], -math.pi / 2, width / 2.)
    end4 = rotate_and_move(points[0], points[1], math.pi / 2, width / 2.)
    pts.append(end1)
    for i in range(1, len(points) - 1):
        angle = angle_between(points[i - 1], points[i], points[i + 1])
        if angle > rad(10) or angle < -rad(10):
            dist = (width / 2.) / math.sin(angle / 2)
        else:
            print(angle)
            dist = 0
        p1 = rotate_and_move(points[i], points[i - 1], angle / 2, dist)
        pts.append(p1)
    pts.extend([end2, end3])
    for i in reversed(range(1, len(points) - 1)):
        pts.append(rotated_point(pts[i], points[i], math.pi))
    pts.append(end4)
    return pts


def is_clockwise(points):
    """Determine if a set of polygon points goes in clockwise or counterclockwise direction.

    If edges cross, it gives the more prominent direction.

    """
    p = points + [points[0]]
    edge_vals = [(p[i+1][0] - p[i][0]) * (p[i+1][1] + p[i][1]) for i
                 in range(len(points))]
    return sum(edge_vals) > 0
