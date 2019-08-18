"""
param.py
========
Define parameter objects that incorporate randomness.

"""

import numpy as np
from typing import Union, Callable


class Param:
    """Objects to represent fixed or random parameters for shapes.

    Create ``Param`` objects for fixed values, value lists, or
    arbitrary functions.  For random distributions, use a specific
    class that inherits from ``Param``.

    Args:
        x: A value, list, or a function that takes no arguments and
          returns a value.

    """

    def __init__(self, x: Union[str, float, list, Callable], static: bool = True):
        if type(x) is list:
            self.choices = x
            self.function = None
            # self.value = lambda: np.random.choice(self.choices)
            # try:
            #     self.mean = sum(x) / len(x)
            # except TypeError:
            #     True
        elif callable(x):
            self.function = x
            self.choices = None
            # self.value = x()
        else:
            self.value = x
            self.choices = None
            self.function = None
        #     self.mean = x
        self.static = static
        self.t_prev = -1

    def __add__(self, other):
        return Sum(self, other)

    def __radd__(self, other):
        return Sum(other, self)

    def __sub__(self, other):
        return Difference(self, other)

    def __rsub__(self, other):
        return Difference(other, self)

    def __mul__(self, other):
        return Product(self, other)

    def __rmul__(self, other):
        return Product(other, self)

    def __truediv__(self, other):
        return Quotient(self, other)

    def __rtruediv__(self, other):
        return Quotient(other, self)

    # def values(self, n):
    #     return [self.value() for i in range(n)]

    # def state(self, t):
    #     if t == self.t_prev:
    #         return self.value
    #     else:
    #         assert t == self.t_prev + 1
    #         self.value = self.value()
    #         self.t_prev = t
    #         return self.value
    def state(self, t: int = 0):
        if (t > self.t_prev) and (t == 0 or not self.static):
            assert t == self.t_prev + 1
            if self.choices is not None:
                self.value = np.random.choice(self.choices)
            elif self.function is not None:
                self.value = self.function()
            self.t_prev = t
        return self.value


class Uniform(Param):
    """Parameters with uniformly random distributions.

    Args:
        min: The lower bound.
        max: The upper bound.
        static: If set to false, the value will be recomputed for each
          frame.

    """

    def __init__(self, min: float = 0, max: float = 1, static: bool = True):
        self.min = min
        self.max = max
        self.static = static
        # self.mean = (min + max) / 2
        self.t_prev = -1

    # def value(self):
    #     """Generate a value."""
    #     return np.random.uniform(self.min, self.max)

    def state(self, t: int = 0):
        if (t > self.t_prev) and (t == 0 or not self.static):
            assert t == self.t_prev + 1
            self.value = np.random.uniform(self.min, self.max)
            self.t_prev = t
        return self.value


class Normal(Param):
    """Parameters with Gaussian (normal) distributions.

    Args:
        mean: The distribution's mean.
        stdev: The distribution's standard deviation.

    """

    def __init__(self, mean: float = 0, stdev: float = 1, static: bool = True):
        self.mean = mean
        self.stdev = stdev
        self.static = static
        self.t_prev = -1

    # def value(self):
    #     """Generate a value."""
    #     return np.random.normal(self.mean, self.stdev)

    def state(self, t: int = 0):
        if (t > self.t_prev) and (t == 0 or not self.static):
            assert t == self.t_prev + 1
            self.value = np.random.normal(self.mean, self.stdev)
            self.t_prev = t
        return self.value


class Exponential(Param):
    """Parameters with Exponential distributions.

    Args:
        mean: The distribution's mean.
        stdev: The distribution's standard deviation.
        sigma: How many standard deviations from the mean to clip values.

    """

    def __init__(self, mean: float = 1, stdev: float = 1, sigma: float = 2, static: bool = True):
        self.mean = mean
        self.stdev = stdev
        self.static = static
        self.t_prev = -1

    # def value(self):
    #     """Generate a value."""
    #     x = (self.mean - self.stdev) + np.random.exponential(self.stdev)
    #     return x

    def state(self, t: int = 0):
        if (t != self.t_prev) and (t == 0 or not self.static):
            assert t == self.t_prev + 1
            self.value = (self.mean - self.stdev) + np.random.exponential(self.stdev)
            self.t_prev = t
        return self.value


class Sum(Param):
    """"""

    def __init__(self, *params):
        assert len(params) > 0
        self.params = [make_param(p) for p in params]
        self.t_prev = -1

    def state(self, t: int = 0):
        if t != self.t_prev:
            assert t == self.t_prev + 1
            self.value = sum([param.state(t) for param in self.params])
            self.t_prev = t
        return self.value


class Difference(Param):
    """"""

    def __init__(self, first, second):
        self.first = make_param(first)
        self.second = make_param(second)
        self.t_prev = -1

    def state(self, t: int = 0):
        if t != self.t_prev:
            assert t == self.t_prev + 1
            self.value = self.first.state(t) - self.second.state(t)
            self.t_prev = t
        return self.value


class Product(Param):
    """"""

    def __init__(self, *params):
        assert len(params) > 0
        self.params = [make_param(p) for p in params]
        self.t_prev = -1

    def state(self, t: int = 0):
        if t != self.t_prev:
            assert t == self.t_prev + 1
            self.value = 1
            for val in [param.state(t) for param in self.params]:
                self.value *= val
            self.t_prev = t
        return self.value


class Quotient(Param):
    """"""

    def __init__(self, dividend, divisor):
        self.dividend = make_param(dividend)
        self.divisor = make_param(divisor)
        self.t_prev = -1

    def state(self, t: int = 0):
        if t != self.t_prev:
            assert t == self.t_prev + 1
            self.value = self.dividend.state(t) / self.divisor.state(t)
            self.t_prev = t
        return self.value


class Clip(Param):
    """"""

    def __init__(self, param, min, max):
        self.param = make_param(param)
        self.min = make_param(min)
        self.max = make_param(max)
        self.t_prev = -1

    def state(self, t: int = 0):
        if t != self.t_prev:
            assert t == self.t_prev + 1
            self.value = max(
                self.min.state(t), min(self.param.state(t), self.max.state(t))
            )
            self.t_prev = t
        return self.value


class Dynamic(Param):
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
        start: [float, Param] = None,
        delta: Union[float, Param] = None,
        ratio: Union[float, Param] = None,
        min: Union[float, Param] = None,
        max: Union[float, Param] = None,
    ):
        self.start = make_param(start)
        self.delta = make_param(delta) if delta is not None else None
        self.ratio = make_param(ratio) if ratio is not None else None
        self.min = make_param(min)
        self.max = make_param(max)
        self.t_prev = -1

    def state(self, t: int = 0):
        if t == self.t_prev:
            return self.value
        elif t == 0:
            self.value = self.start.state(t)
            # Initialize delta/ratio so they get their t=0 values.
            if self.delta is not None:
                self.delta.state(t)
            if self.ratio is not None:
                self.ratio.state(t)
            self.t_prev = t
            return self.value
        else:
            assert t == self.t_prev + 1
            if self.delta is not None:
                self.value += self.delta.state(t)
            if self.ratio is not None:
                self.value *= self.ratio.state(t)
            mn, mx = self.min.state(t), self.max.state(t)
            if mn is not None:
                self.value = max(self.value, mn)
            if mx is not None:
                self.value = min(self.value, mx)
            self.t_prev = t
            return self.value


# class Cyclical(Param):
#     """Parameters that oscillate between values.

#     Its low value, high value, and period can be Params to add
#     randomness to the cycle.

#     Args:
#         low: The minimum value (wave trough).
#         high: The maximum value (wave peak).
#         period: The number of values returned per oscillation.  It
#           need not be an integer.
#         phase: The starting offset of sine oscillation in degrees.
#           The default of zero starts halfway between ``low`` and
#           ``high`` and increases.

#     """

#     def __init__(
#         self, low: float = -1, high: float = 1, period: float = 8, phase: float = 0
#     ):
#         self.low = make_param(low)
#         self.high = make_param(high)
#         self.period = make_param(period)
#         # self.next = (self.low.value() + self.high.value()) / 2
#         self.theta = rad(fixed_value(phase))
#         self.next = self._wave_value()
#         self.t_prev = -1

#     def _wave_value(self):
#         val = (np.sin(self.theta) + 1) / 2  # Scale to 0-1 range.
#         high, low = self.high.value(), self.low.value()
#         return val * (high - low) + low

#     def value(self):
#         """Generate a value."""
#         val = self.next
#         self.theta += 2 * np.pi / self.period.value()
#         self.next = self._wave_value()
#         return val


def fixed_value(x: Union[float, str, Param], t: int = 0) -> Union[float, str]:
    """Get a fixed value even if a ``Param`` object is supplied.

    Args:
        x: An object.
        t: The current timepoint.

    """
    if isinstance(x, Param):
        return x.state(t)
    else:
        return x


def make_param(x: Union[float, str, Param]) -> Param:
    """Get a ``Param`` object even if something else is supplied.

    """
    if isinstance(x, Param):
        return x
    else:
        return Param(x)
