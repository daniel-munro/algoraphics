"""
point.py
========
Define objects that represent dynamic 2D points.

"""

from typing import Tuple, Union
from .geom import endpoint, rad, rotated_point, scaled_point
from .param import Param, Uniform, make_param, fixed_value


class Point:
    """A representation of a dynamic location in 2D space.

    Args:
        ref: The reference or starting point.
        direction: A param giving directions (in degrees) of generated
          points relative to ref.  By default the direction is
          uniformly random.
        distance: A param giving distances of generated points relative to ref.

    """

    def __init__(self, point: Union[Tuple[float, float], "Point"]):
        self.point = point
        self.t_prev = -1

    def __add__(self, other):
        return Translation(self, other)

    def __radd__(self, other):
        return Translation(other, self)

    def state(self, t: int = 0):
        if t != self.t_prev:
            assert t == self.t_prev + 1
            if type(self.point) is tuple:
                self.value = (fixed_value(self.point[0], t), fixed_value(self.point[1], t))
            else:
                self.value = self.point.state(t)
            self.t_prev = t
        return self.value


class Move(Point):
    """

    Args:
        ref: The reference or starting point.
        direction: A param giving directions (in degrees) of generated
          points relative to ref.  By default the direction is
          uniformly random.
        distance: A param giving distances of generated points relative to ref.

    """

    def __init__(
        self,
        ref: Union[Tuple[float, float], "Point"],
        direction: Param = None,
        distance: Param = 0,
    ):
        self.ref = make_point(ref)
        if direction is None:
            self.direction = Uniform(0, 360)
        else:
            self.direction = make_param(direction)
        self.distance = make_param(distance)
        self.t_prev = -1

    def state(self, t: int = 0):
        if t != self.t_prev:
            assert t == self.t_prev + 1
            self.value = endpoint(
                self.ref.state(t), rad(self.direction.state(t)), self.distance.state(t)
            )
            self.t_prev = t
        return self.value


class Translation(Point):
    def __init__(self, start, move):
        self.start = make_point(start)
        self.move = make_point(move)
        self.t_prev = -1

    def state(self, t: int = 0):
        if t != self.t_prev:
            assert t == self.t_prev + 1
            p1 = self.start.state(t)
            p2 = self.move.state(t)
            self.value = (p1[0] + p2[0], p1[1] + p2[1])
            self.t_prev = t
        return self.value


class Rotation(Point):
    def __init__(self, start, pivot, angle):
        self.start = make_point(start)
        self.pivot = make_point(pivot)
        self.angle = make_param(angle)
        self.t_prev = -1

    def state(self, t: int = 0):
        if t != self.t_prev:
            assert t == self.t_prev + 1
            start = self.start.state(t)
            pivot = self.pivot.state(t)
            angle = self.angle.state(t)
            self.value = rotated_point(start, pivot, angle)
        return self.value


class Scaling(Point):
    def __init__(self, start, cx: Param, cy: Param = None):
        self.start = make_point(start)
        self.cx = make_param(cx)
        self.cy = cx if cy is None else make_param(cy)
        self.t_prev = -1

    def state(self, t: int = 0):
        if t != self.t_prev:
            assert t == self.t_prev + 1
            start = self.start.state(t)
            cx = self.cx.state(t)
            cy = self.cy.state(t)
            self.value = scaled_point(start, cx, cy)
        return self.value


def make_point(x: Union[Point, Point]) -> Point:
    """Get a ``Point`` object even if a tuple is supplied.

    """
    if isinstance(x, Point):
        return x
    else:
        return Point(x)
