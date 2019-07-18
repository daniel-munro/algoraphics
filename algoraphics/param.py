"""
param.py
========
Define parameter objects that incorporate randomness.

"""

import numpy as np
from copy import deepcopy
from typing import Union, Callable, Tuple

from .geom import endpoint, rad

Number = Union[int, float]
Point = Tuple[Number, Number]


class Param:
    """Objects to represent fixed or random parameters for shapes.

    Create ``Param`` objects for fixed values, value lists, or
    arbitrary functions.  For random distributions, use a specific
    class that inherits from ``Param``.

    Args:
        x: A value, list, or a function that takes no arguments and
          returns a value.

    """

    def __init__(self, x: Union[str, float, int, list, Callable]):
        if type(x) is list:
            self.choices = x
            self.value = lambda: np.random.choice(self.choices)
            try:
                self.mean = sum(x) / len(x)
            except TypeError:
                True
        elif callable(x):
            self.value = x
        else:
            self.value = lambda: x
            self.mean = x

    def values(self, n):
        return [self.value() for i in range(n)]


class Uniform(Param):
    """Parameters with uniformly random distributions.

    Args:
        min: The lower bound.
        max: The upper bound.

    """

    def __init__(self, min: Number = 0, max: Number = 1):
        self.min = min
        self.max = max
        self.mean = (min + max) / 2

    def value(self):
        """Generate a value."""
        return np.random.uniform(self.min, self.max)


class Normal(Param):
    """Parameters with Gaussian (normal) distributions.

    Args:
        mean: The distribution's mean.
        stdev: The distribution's standard deviation.

    """

    def __init__(self, mean: Number = 0, stdev: Number = 1):
        self.mean = mean
        self.stdev = stdev

    def value(self):
        """Generate a value."""
        return np.random.normal(self.mean, self.stdev)


class Exponential(Param):
    """Parameters with Exponential distributions.

    Args:
        mean: The distribution's mean.
        stdev: The distribution's standard deviation.
        sigma: How many standard deviations from the mean to clip values.

    """

    def __init__(self, mean: Number = 1, stdev: Number = 1, sigma: Number = 2):
        self.mean = mean
        self.stdev = stdev
        self.min = mean - sigma * stdev
        self.max = mean + sigma * stdev

    def value(self):
        """Generate a value."""
        x = (self.mean - self.stdev) + np.random.exponential(self.stdev)
        x = np.clip(x, self.min, self.max)
        return x


class Delta(Param):
    """Parameters whose values depend on the previous value.

    Provide a Param or number for ``delta`` which will be added to the
    previously generated value to get the next one.  Or, provide a
    ``ratio`` Param or number to multiply to each previous value.

    Passing a randomized ``Param`` object to ``delta`` or ``ratio``
    will result in a random walk.  These ``Param`` objects can
    themselves have a ``delta``/``ratio`` argument, resulting in
    higher-order random walks.

    Args:
        start: The starting value, which can be obtained from a Param.
        delta: A value to add to the previous value to get the next.
        ratio: Similar to delta, but is multiplied by, rather than
          added to, the previous value to get the next.
        min: The smallest allowable value.
        max: The largest allowable value.

    """

    def __init__(
        self,
        start: [Number, Param] = None,
        delta: Union[Number, Callable, Param] = None,
        ratio: Union[Number, Callable, Param] = None,
        min: Union[Number, Param] = None,
        max: Union[Number, Param] = None,
    ):
        assert delta is not None or ratio is not None, "Provide delta or ratio."
        self.min = make_param(min)
        self.max = make_param(max)
        if start is not None:
            self.next = start
        elif min is not None and max is not None:
            self.next = np.random.uniform(self.min.value(), self.max.value())
        else:
            self.next = 0 if delta is not None else 1
        self.delta = delta
        self.ratio = ratio
        if delta is not None:
            self.value = self._value_with_delta
        else:
            self.value = self._value_with_ratio

    def _value_with_delta(self):
        """Add ``delta`` to get the next value."""
        this_delta = fixed_value(self.delta)
        val = self.next
        new = val + this_delta
        mn, mx = self.min.value(), self.max.value()
        if mn is not None:
            new = max(new, mn)
        if mx is not None:
            new = min(new, mx)
        self.next = new
        return val

    def _value_with_ratio(self):
        """Multiply by ``ratio`` to get the next value."""
        this_ratio = fixed_value(self.ratio)
        val = self.next
        new = val * this_ratio
        mn, mx = self.min.value(), self.max.value()
        if mn is not None:
            new = max(new, mn)
        if mx is not None:
            new = min(new, mx)
        self.next = new
        return val

    def values(self, n):
        return [self.value() for i in range(n)]


class Cyclical(Param):
    """Parameters that oscillate between values.

    Its low value, high value, and period can be Params to add
    randomness to the cycle.

    Args:
        low: The minimum value (wave trough).
        high: The maximum value (wave peak).
        period: The number of values returned per oscillation.  It
          need not be an integer.
        phase: The starting offset of sine oscillation in degrees.
          The default of zero starts halfway between ``low`` and
          ``high`` and increases.

    """

    def __init__(
        self, low: Number = -1, high: Number = 1, period: Number = 8, phase: Number = 0
    ):
        self.low = make_param(low)
        self.high = make_param(high)
        self.period = make_param(period)
        # self.next = (self.low.value() + self.high.value()) / 2
        self.theta = rad(fixed_value(phase))
        self.next = self._wave_value()

    def _wave_value(self):
        val = (np.sin(self.theta) + 1) / 2  # Scale to 0-1 range.
        high, low = self.high.value(), self.low.value()
        return val * (high - low) + low

    def value(self):
        """Generate a value."""
        val = self.next
        self.theta += 2 * np.pi / self.period.value()
        self.next = self._wave_value()
        return val


class Place:
    """An object that generates points with respect to a reference point.

    It is the 2D version of Param, and uses polar coordinates.

    Args:
        ref: The reference or starting point.
        direction: A param giving directions (in degrees) of generated
          points relative to ref.  By default the direction is
          uniformly random.
        distance: A param giving distances of generated points relative to ref.

    """

    def __init__(self, ref: Point, direction: Param = None, distance: Param = 0):
        self.ref = fixed_value(ref)
        if direction is None:
            self.direction = Uniform(0, 360)
        else:
            self.direction = make_param(direction)
        self.distance = make_param(distance)

    def value(self):
        """Generate points relative to reference."""
        return endpoint(self.ref, rad(self.direction.value()), self.distance.value())

    def values(self, n):
        return [self.value() for i in range(n)]


class Wander(Place):
    """An object that generates points relative to the previous point.

    Just as Place is the 2D version of Param, Wander is the 2D version
    of Delta.

    Args:
        delta_direc: A param giving the direction to move in e

    """

    def __init__(
        self,
        start: Point,
        direction: Union[Number, Callable, "Param"] = 0,
        distance: Union[Number, Callable, "Param"] = 0,
    ):
        self.next = (fixed_value(start[0]), fixed_value(start[1]))
        self.direction = make_param(direction)
        self.distance = make_param(distance)

    def value(self):
        """Move to get the next value."""
        pt = self.next
        new = endpoint(pt, rad(self.direction.value()), self.distance.value())
        self.next = new
        return pt


def fixed_value(x: Union[Number, str, Param, Place]) -> Union[Number, str]:
    """Get a fixed value if a ``Param`` object is supplied.

    """
    if isinstance(x, Param) or isinstance(x, Place):
        return x.value()
    else:
        return x


def make_param(x: Union[Number, str, Param]) -> Param:
    """Get a ``Param`` object even if something else is supplied.

    If a ``Param`` object is supplied, a deep copy is generated in
    case it has a ``delta`` or ``ratio`` and is being reused.

    """
    if isinstance(x, Delta):
        return deepcopy(x)  # Copy in case it is reused.
    elif isinstance(x, Param):
        return x
    else:
        return Param(x)


def make_place(x: Union[Point, Place]) -> Param:
    """Get a ``Place`` object even if a fixed point is supplied.

    """
    if isinstance(x, Wander):
        return deepcopy(x)  # Copy in case it is reused.
    elif isinstance(x, Place):
        return x
    else:
        return Place(x)
