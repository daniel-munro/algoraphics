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

    Create ``Param`` objects for fixed values, value lists, arbitrary
    functions, and parameters with ``delta`` or ``ratio``.  For random
    distributions, use a specific class that inherits from ``Param``.

    If ``delta`` or ``ratio`` is supplied, ``x`` is the starting value
    if supplied.  Otherwise, if ``min`` and ``max`` are supplied, the
    starting value will be chosen uniformly randomly between them.
    Otherwise, the starting value will be 0 (delta) or 1 (ratio).

    Passing a randomized ``Param`` object to ``delta`` or ``ratio``
    will result in a random walk.  These ``Param`` objects can
    themselves have a ``delta``/``ratio`` argument, resulting in
    higher-order random walks.

    Args:
        x: A value, list, or function that takes no arguments and
          returns a value.
        delta: A value to add to the previous value to get the next.
        ratio: Similar to delta, but is multiplied by, rather than
          added to, the previous value to get the next.
        min: The smallest allowable value when ``delta`` or ``ratio`` is used.
        max: The largest allowable value when ``delta`` or ``ratio`` is used.

    """
    def __init__(self, x: Union[str, float, int, list, Callable] = None,
                 delta: Union[Number, Callable, 'Param'] = None,
                 ratio: Union[Number, Callable, 'Param'] = None,
                 min: Number = None, max: Number = None):
        if delta is not None or ratio is not None:
            if x is not None:
                self.next = x
            elif min is not None and max is not None:
                self.next = np.random.uniform(min, max)
            else:
                self.next = 0 if delta is not None else 1
                # raise TypeError("For a Param with delta or ratio, provide "
                #                 + "starting value or min and max.")
        elif type(x) is list:
            self.values = x
            self.value = lambda: np.random.choice(self.values)
            try:
                self.mean = sum(x) / len(x)
            except TypeError:
                True
        elif callable(x):
            self.value = x
        else:
            if min is not None and max is not None:
                raise ValueError("Use min/max only with delta/ratio, or pass "
                                 + "to Uniform.")
            self.value = lambda: x
            self.mean = x

        if delta is not None:
            self.min = min
            self.max = max
            self.delta = delta
            # self.next = self.value()
            self.value = self._value_with_delta
        elif ratio is not None:
            self.min = min
            self.max = max
            self.ratio = ratio
            # self.next = self.value()
            self.value = self._value_with_ratio

    def _value_with_delta(self):
        """Add ``delta`` to get the next value."""
        this_delta = fixed_value(self.delta)
        val = self.next
        new = val + this_delta
        if self.min is not None:
            new = max(new, self.min)
        if self.max is not None:
            new = min(new, self.max)
        self.next = new
        return val

    def _value_with_ratio(self):
        """Multiply by ``ratio`` to get the next value."""
        this_ratio = fixed_value(self.ratio)
        val = self.next
        new = self.next * this_ratio
        if self.min is not None:
            new = max(new, self.min)
        if self.max is not None:
            new = min(new, self.max)
        self.next = new
        return val

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
    def __init__(self, mean: Number = 1, stdev: Number = 1, sigma:
                 Number = 2):
        self.mean = mean
        self.stdev = 1
        self.min = mean - sigma * stdev
        self.max = mean + sigma * stdev

    def value(self):
        """Generate a value."""
        x = (self.mean - self.stdev) + np.random.exponential(self.stdev)
        # x = np.clip(x, self.min, self.max)
        return x


class Cyclical(Param):
    """Parameters that oscillate between values.

    Args:
        low: The minimum value (wave trough).
        high: The maximum value (wave peak).
        period: The number of values returned per oscillation.  It
          need not be an integer.
        phase: The starting offset of sine oscillation in degrees.
          The default of zero starts halfway between ``low`` and
          ``high`` and increases.

    """
    def __init__(self, low: Number = -1, high: Number = 1, period:
                 Number = 8, phase = 0):
        self.low = make_param(low)
        self.high = make_param(high)
        self.period = make_param(period)
        # self.next = (self.low.value() + self.high.value()) / 2
        self.theta = rad(fixed_value(phase))
        self.next = self._wave_value()

    def _wave_value(self):
        val = (np.sin(self.theta) + 1) / 2 # Scale to 0-1 range.
        high, low = self.high.value(), self.low.value()
        return val * (high - low) + low

    def value(self):
        """Generate a value."""
        val = self.next
        self.theta += 2 * np.pi / self.period.value()
        self.next = self._wave_value()
        return val


def fixed_value(x: Union[Number, str, Param]) -> Union[Number, str]:
    """Get a fixed value if a ``Param`` object is supplied.

    """
    if isinstance(x, Param) or isinstance(x, Place):
        return x.value()
    else:
        return x


def make_param(x: Union[Number, str, Param]) -> Param:
    """Get a ``Param`` object if something else is supplied.

    If a ``Param`` object is supplied, a deep copy is generated in
    case it has a ``delta`` or ``ratio`` and is being reused.

    """
    if isinstance(x, Param) or isinstance(x, Place):
        # Copy in case it is random walk and user reuses it.
        return(deepcopy(x))
    else:
        return Param(x)


class Place:
    """An object that generates points with respect to a reference point.

    Args:
        ref: The reference or starting point.
        direction: A param giving directions (in degrees) of generated
          points relative to ref.
        distance: A param giving distances of generated points relative to ref.

    """
    def __init__(self, ref: Point, direction: Param = None, distance:
                 Param = None):
        self.ref = ref
        self.direction = make_param(direction)
        self.distance = make_param(distance)
            
    def value(self):
        """Generate points relative to reference."""
        return endpoint(self.ref, rad(self.direction.value()),
                        self.distance.value())

    def values(self, n):
        return [self.value() for i in range(n)]


class Wander(Place):
    """
        delta_direc: A param giving the direction to move in e

    """
    def __init__(self, start: Point,
                 direction: Union[Number, Callable, 'Param'] = None,
                 distance: Union[Number, Callable, 'Param'] = None):
        self.next = (fixed_value(start[0]), fixed_value(start[1]))
        self.direction = make_param(direction)
        self.distance = make_param(distance)
    def value(self):
        """Move to get the next value."""
        pt = self.next
        new = endpoint(pt, rad(self.direction.value()), self.distance.value())
        self.next = new
        return pt
