"""
text.py
=======
Generate text in the form of shapes or SVG text.

"""

import math
import numpy as np
from typing import Union, Tuple, List

from .main import shuffled
from .geom import (
    points_on_line,
    points_on_arc,
    scale_points,
    translate_points,
    horizontal_range,
    endpoint,
    deg,
    jitter_points,
)
from .shapes import circle, spline, set_style
from .color import Color

Number = Union[int, float]
Point = Tuple[Number, Number]


def char_points(char: str, start: Point, h: Number, spacing:
                Number) -> List[List[Point]]:
    """Generate points along a character shape.

    Args:
        char: A character.
        start: The lower-left point of the character bounds.
        h: The line height.
        spacing: Distance between adjacent points.

    Returns:
        A list of lists of points.  Each list of points corresponds to
        a pen stroke (i.e. what can be drawn without lifting the pen).

    """
    sp = spacing / h      # Used before scaling character to height h.
    points = []

    if char == 'A':
        p1 = (0, 0)
        p2 = (0.35, 1)
        p3 = (0.7, 0)
        p4 = (0.25 * 0.7, 0.5)
        p5 = (0.75 * 0.7, 0.5)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        points.append(x)

        points.append(points_on_line(p4, p5, sp))

    elif char == 'B':
        p1 = (0, 0)
        p2 = (0, 1)
        p3 = (0.3, 1)
        c1 = (0.3, 0.75)
        p4 = (0.3, 0.5)
        p5 = (0, 0.5)
        c2 = (0.3, 0.25)
        p6 = (0.3, 0)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        x.extend(points_on_arc(c1, 0.25, 90, -90, sp))
        x.extend(points_on_line(p4, p5, sp))
        points.append(x)

        x = points_on_arc(c2, 0.25, 90, -90, sp)
        x.extend(points_on_line(p6, p1, sp))
        points.append(x)

    elif char == 'C':
        r = 0.35
        p1 = (0, 1 - r)
        p2 = (0, r)

        x = points_on_arc((r, 1 - r), r, 45, 180, sp)
        x.extend(points_on_line(p1, p2, sp))
        x.extend(points_on_arc((r, r), r, 180, 315, sp))
        points.append(x)

    elif char == 'D':
        p1 = (0, 1)
        p2 = (0, 0)
        p3 = (0.2, 0)
        c = (0.2, 0.5)
        p4 = (0.2, 1)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        x.extend(points_on_arc(c, 0.5, -90, 90, sp))
        x.extend(points_on_line(p4, p1, sp))
        points.append(x)

    elif char == 'E':
        p1 = (0.6, 1)
        p2 = (0, 1)
        p3 = (0, 0)
        p4 = (0.6, 0)
        p5 = (0, 0.5)
        p6 = (0.6, 0.5)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        x.extend(points_on_line(p3, p4, sp))
        points.append(x)

        points.append(points_on_line(p5, p6, sp))

    elif char == 'F':
        p1 = (0, 0)
        p2 = (0, 1)
        p3 = (0.6, 1)
        p4 = (0, 0.5)
        p5 = (0.6, 0.5)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        points.append(x)

        points.append(points_on_line(p4, p5, sp))

    elif char == 'G':
        r = 0.4
        c1 = (r, 1 - r)
        p1 = (0, 1 - r)
        p2 = (0, r)
        c2 = (r, r)
        p3 = (2 * r, r)

        x = points_on_arc(c1, r, 30, 180, sp)
        x.extend(points_on_line(p1, p2, sp))
        x.extend(points_on_arc(c2, r, 180, 360, sp))
        x.extend(points_on_line(p3, c2, sp))
        points.append(x)

    elif char == 'H':
        p1 = (0, 1)
        p2 = (0, 0)
        p3 = (0.7, 1)
        p4 = (0.7, 0)
        p5 = (0, 0.5)
        p6 = (0.7, 0.5)

        points.append(points_on_line(p1, p2, sp))

        points.append(points_on_line(p3, p4, sp))

        points.append(points_on_line(p5, p6, sp))

    elif char == 'I':
        p1 = (0, 1)
        p2 = (0.5, 1)
        p3 = (0, 0)
        p4 = (0.5, 0)
        p5 = (0.25, 1)
        p6 = (0.25, 0)

        points.append(points_on_line(p1, p2, sp))

        points.append(points_on_line(p3, p4, sp))

        points.append(points_on_line(p5, p6, sp))

    elif char == 'J':
        r = 0.25
        p1 = (2 * r, 1)
        p2 = (2 * r, r)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_arc((r, r), r, 360, 180, sp))
        points.append(x)

    elif char == 'K':
        x = points_on_line((0, 1), (0, 0), sp)
        points.append(x)

        x = points_on_line((0.6, 1), (0, 0.5), sp)
        x.extend(points_on_line((0, 0.5), (0.6, 0), sp))
        points.append(x)

    elif char == 'L':
        p1 = (0, 1)
        p2 = (0, 0)
        p3 = (0.6, 0)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        points.append(x)

    elif char == 'M':
        p1 = (0, 0)
        p2 = (0, 1)
        p3 = (0.35, 0.5)
        p4 = (0.7, 1)
        p5 = (0.7, 0)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        x.extend(points_on_line(p3, p4, sp))
        x.extend(points_on_line(p4, p5, sp))
        points.append(x)

    elif char == 'N':
        p1 = (0, 0)
        p2 = (0, 1)
        p3 = (0.7, 0)
        p4 = (0.7, 1)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        x.extend(points_on_line(p3, p4, sp))
        points.append(x)

    elif char == 'O':
        r = 0.4
        p1 = (0, 1 - r)
        p2 = (0, r)
        c1 = (r, r)
        p3 = (2 * r, r)
        p4 = (2 * r, 1 - r)
        c2 = (r, 1 - r)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_arc(c1, r, 180, 360, sp))
        x.extend(points_on_line(p3, p4, sp))
        x.extend(points_on_arc(c2, r, 0, 180, sp))
        points.append(x)

    elif char == 'P':
        p1 = (0, 0)
        p2 = (0, 1)
        p3 = (0.3, 1)
        c = (0.3, 0.75)
        p4 = (0.3, 0.5)
        p5 = (0, 0.5)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        x.extend(points_on_arc(c, 0.25, 90, -90, sp))
        x.extend(points_on_line(p4, p5, sp))
        points.append(x)

    elif char == 'Q':
        r = 0.4
        p1 = (0, 1 - r)
        p2 = (0, r)
        c1 = (r, r)
        p3 = (2 * r, r)
        p4 = (2 * r, 1 - r)
        c2 = (r, 1 - r)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_arc(c1, r, 180, 360, sp))
        x.extend(points_on_line(p3, p4, sp))
        x.extend(points_on_arc(c2, r, 0, 180, sp))
        points.append(x)

        x = points_on_line(c1, (2 * r, 0), sp)
        points.append(x)

    elif char == 'R':
        p1 = (0, 0)
        p2 = (0, 1)
        p3 = (0.3, 1)
        c = (0.3, 0.75)
        p4 = (0.3, 0.5)
        p5 = (0, 0.5)
        p6 = (0.55, 0)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        x.extend(points_on_arc(c, 0.25, 90, -90, sp))
        x.extend(points_on_line(p4, p5, sp))
        points.append(x)

        points.append(points_on_line(p4, p6, sp))

    elif char == 'S':
        r = 0.25
        le = 0.15
        c1 = (r + le, 3 * r)
        c2 = (r, 3 * r)
        c3 = (r + le, r)
        c4 = (r, r)
        p1 = (r + le, 4 * r)
        p2 = (r, 4 * r)
        p3 = (r, 2 * r)
        p4 = (r + le, 2 * r)
        p5 = (r + le, 0)
        p6 = (r, 0)

        x = points_on_arc(c1, r, 0, 90, sp)
        x.extend(points_on_line(p1, p2, sp))
        x.extend(points_on_arc(c2, r, 90, 270, sp))
        x.extend(points_on_line(p3, p4, sp))
        x.extend(points_on_arc(c3, r, 90, -90, sp))
        x.extend(points_on_line(p5, p6, sp))
        x.extend(points_on_arc(c4, r, 270, 180, sp))
        points.append(x)

    elif char == 'T':
        p1 = (0, 1)
        p2 = (0.7, 1)
        p3 = (0.35, 1)
        p4 = (0.35, 0)

        points.append(points_on_line(p1, p2, sp))

        points.append(points_on_line(p3, p4, sp))

    elif char == 'U':
        r = 0.35
        x = points_on_line((0, 1), (0, r), sp)
        x.extend(points_on_arc((r, r), r, 180, 360, sp))
        x.extend(points_on_line((2 * r, r), (2 * r, 1), sp))
        points.append(x)

    elif char == 'V':
        p1 = (0, 1)
        p2 = (0.35, 0)
        p3 = (0.7, 1)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        points.append(x)

    elif char == 'W':
        dx = 0.25
        p1 = (0, 1)
        p2 = (dx, 0)
        p3 = (2 * dx, 1)
        p4 = (3 * dx, 0)
        p5 = (4 * dx, 1)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        x.extend(points_on_line(p3, p4, sp))
        x.extend(points_on_line(p4, p5, sp))
        points.append(x)

    elif char == 'X':
        x = points_on_line((0, 1), (0.7, 0), sp)
        x.extend(points_on_line((0, 0), (0.7, 1), sp))
        points.append(x)

    elif char == 'Y':
        p1 = (0, 1)
        p2 = (0.35, 0.5)
        p3 = (0.7, 1)
        p4 = (0.35, 0)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        points.append(x)

        x = points_on_line(p2, p4, sp)
        points.append(x)

    elif char == 'Z':
        p1 = (0, 1)
        p2 = (0.7, 1)
        p3 = (0, 0)
        p4 = (0.7, 0)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        x.extend(points_on_line(p3, p4, sp))
        points.append(x)

    elif char == 'a':
        p1 = (0.5, 0.6)
        r1 = 0.2 * 2 ** 0.5
        c1 = (0.3, 0.6 - r1 / 2 ** 0.5)
        p2 = (0.5, 0)
        p3 = (0.2, 0)
        r2 = 0.2
        c2 = (r2, r2)
        p4 = (0.2, 2 * r2)
        p5 = (0.5, 2 * r2)

        x = points_on_arc(c1, r1, 135, 45, sp)
        x.extend(points_on_line(p1, p2, sp))
        x.extend(points_on_line(p2, p3, sp))
        x.extend(points_on_arc(c2, r2, 270, 90, sp))
        x.extend(points_on_line(p4, p5, sp))
        points.append(x)

    elif char == 'b':
        r = 0.35
        c = (r / 2 ** 0.5, r)

        points.append(points_on_line((0, 1), (0, 0), sp))
        points.append(points_on_arc(c, r, 135, -135, sp))

    elif char == 'c':
        r = 0.35
        points.append(points_on_arc((r, r), r, 45, 315, sp))

    elif char == 'd':
        r = 0.35
        p1 = (r + r / 2 ** 0.5, 1)
        p2 = (p1[0], 0)

        points.append(points_on_line(p1, p2, sp))
        points.append(points_on_arc((r, r), r, 45, 315, sp))

    elif char == 'e':
        r = 0.35
        p1 = (0, r)
        p2 = (2 * r, r)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_arc((r, r), r, 0, 320, sp))
        points.append(x)

    elif char == 'f':
        r = 0.25
        p1 = (r / 2, 0)
        p2 = (r / 2, 1 - r)
        c = (1.5 * r, 1 - r)
        p3 = (0, 0.7)
        p4 = (c[0], 0.7)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_arc(c, r, 180, 90, sp))
        points.append(x)

        points.append(points_on_line(p3, p4, sp))

    elif char == 'g':
        r1 = 0.35
        c1 = (r1, r1)
        p1 = (r1 + r1 / 2 ** 0.5, 2 * r1)
        p2 = (p1[0], -0.5 * r1)
        r2 = 0.3
        c2 = (p1[0] - r2, p2[1])

        points.append(points_on_arc(c1, r1, 45, 315, sp))

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_arc(c2, r2, 360, 210, sp))
        points.append(x)

    elif char == 'h':
        r = 0.25
        p1 = (0, 1)
        p2 = (0, 0)
        p3 = (2 * r, 0.7 - r)
        p4 = (2 * r, 0)
        c = (r, 0.7 - r)

        points.append(points_on_line(p1, p2, sp))

        x = points_on_arc(c, r, 180, 0, sp)
        x.extend(points_on_line(p3, p4, sp))
        points.append(x)

    elif char == 'i':
        r = 0.05
        p1 = (r, 0.7)
        p2 = (r, 0)
        c = (r, 0.95)

        points.append(points_on_line(p1, p2, sp))
        points.append(points_on_arc(c, r, 0, 360, sp))

    elif char == 'j':
        r1 = 0.25
        p1 = (r1, 0.7)
        p2 = (r1, -0.25)
        c1 = (0, -0.25)
        r2 = 0.05
        c2 = (r1, 0.95)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_arc(c1, r1, 360, 270, sp))
        points.append(x)

        points.append(points_on_arc(c2, r2, 0, 360, sp))

    elif char == 'k':
        p1 = (0, 1)
        p2 = (0, 0)
        p3 = (0.4, 0.7)
        p4 = (0, 0.35)
        p5 = (0.4, 0)

        points.append(points_on_line(p1, p2, sp))

        x = points_on_line(p3, p4, sp)
        x.extend(points_on_line(p4, p5, sp))
        points.append(x)

    elif char == 'l':
        r = 0.25

        x = points_on_line((0, 1), (0, r), sp)
        x.extend(points_on_arc((r, r), r, 180, 270, sp))
        points.append(x)

    elif char == 'm':
        r = 0.18
        p1 = (0, 0.7)
        p2 = (0, 0)
        p3 = (2 * r, 0.7 - r)
        p4 = (2 * r, 0)
        p5 = (4 * r, 0.7 - r)
        p6 = (4 * r, 0)
        c1 = (r, 0.7 - r)
        c2 = (3 * r, 0.7 - r)

        points.append(points_on_line(p1, p2, sp))

        x = points_on_arc(c1, r, 180, 0, sp)
        x.extend(points_on_line(p3, p4, sp))
        points.append(x)

        x = points_on_arc(c2, r, 180, 0, sp)
        x.extend(points_on_line(p5, p6, sp))
        points.append(x)

    elif char == 'n':
        r = 0.25
        p1 = (0, 0.7)
        p2 = (0, 0)
        p3 = (2 * r, 0.7 - r)
        p4 = (2 * r, 0)
        c = (r, 0.7 - r)

        points.append(points_on_line(p1, p2, sp))

        x = points_on_arc(c, r, 180, 0, sp)
        x.extend(points_on_line(p3, p4, sp))
        points.append(x)

    elif char == 'o':
        r = 0.35
        points.append(points_on_arc((r, r), r, 0, 360, sp))

    elif char == 'p':
        r = 0.35
        p1 = (0, 2 * r)
        p2 = (0, -1.5 * r)
        c = (r / 2 ** 0.5, r)

        points.append(points_on_line(p1, p2, sp))
        points.append(points_on_arc(c, r, 135, -135, sp))

    elif char == 'q':
        r = 0.35
        p1 = (r + r / 2 ** 0.5, 2 * r)
        p2 = (p1[0], -1.5 * r)

        points.append(points_on_arc((r, r), r, 45, 315, sp))
        points.append(points_on_line(p1, p2, sp))

    elif char == 'r':
        p1 = (0, 0.7)
        p2 = (0, 0)
        r = 0.25
        c = (r, p1[1] - r)

        points.append(points_on_line(p1, p2, sp))
        points.append(points_on_arc(c, r, 180, 30, sp))

    elif char == 's':
        r = 0.35 / 2
        le = 0.15
        c1 = (r + le, 3 * r)
        c2 = (r, 3 * r)
        c3 = (r + le, r)
        c4 = (r, r)
        p1 = (r + le, 4 * r)
        p2 = (r, 4 * r)
        p3 = (r, 2 * r)
        p4 = (r + le, 2 * r)
        p5 = (r + le, 0)
        p6 = (r, 0)

        x = points_on_arc(c1, r, 0, 90, sp)
        x.extend(points_on_line(p1, p2, sp))
        x.extend(points_on_arc(c2, r, 90, 270, sp))
        x.extend(points_on_line(p3, p4, sp))
        x.extend(points_on_arc(c3, r, 90, -90, sp))
        x.extend(points_on_line(p5, p6, sp))
        x.extend(points_on_arc(c4, r, 270, 180, sp))
        points.append(x)

    elif char == 't':
        r = 0.25
        p1 = (r / 2, 1)
        p2 = (r / 2, r)
        p3 = (0, 0.7)
        p4 = (1.5 * r, p3[1])
        c = (p4[0], r)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_arc(c, r, 180, 270, sp))
        points.append(x)

        points.append(points_on_line(p3, p4, sp))

    elif char == 'u':
        r = 0.25
        p1 = (0, 0.7)
        p2 = (0, r)
        p3 = (2 * r, 0.7)
        p4 = (2 * r, 0)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_arc((r, r), r, 180, 360, sp))
        points.append(x)

        points.append(points_on_line(p3, p4, sp))

    elif char == 'v':
        p1 = (0, 0.7)
        p2 = (0.35, 0)
        p3 = (0.7, 0.7)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        points.append(x)

    elif char == 'w':
        dx = 0.2
        p1 = (0, 0.7)
        p2 = (p1[0] + dx, 0)
        p3 = (p2[0] + dx, 0.7)
        p4 = (p3[0] + dx, 0)
        p5 = (p4[0] + dx, 0.7)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        x.extend(points_on_line(p3, p4, sp))
        x.extend(points_on_line(p4, p5, sp))
        points.append(x)

    elif char == 'x':
        p1 = (0, 0.7)
        p2 = (0.5, 0)
        p3 = (0, 0)
        p4 = (0.5, 0.7)

        points.append(points_on_line(p1, p2, sp))
        points.append(points_on_line(p3, p4, sp))

    elif char == 'y':
        le = 0.35
        p1 = (0, 2 * le)
        p2 = (le, 0)
        p3 = (2 * le, 2 * le)
        p4 = (0.5 * le, -le)
        c = (le / 4, -le + le / (4 * 3 ** 0.5))
        r = le / (2 * 3 ** 0.5)

        points.append(points_on_line(p1, p2, sp))

        x = points_on_line(p3, p4, sp)
        x.extend(points_on_arc(c, r, 330, 210, sp))
        points.append(x)

    elif char == 'z':
        p1 = (0, 0.7)
        p2 = (0.5, 0.7)
        p3 = (0, 0)
        p4 = (0.5, 0)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_line(p2, p3, sp))
        x.extend(points_on_line(p3, p4, sp))
        points.append(x)

    elif char == '0':
        r = 0.25
        p1 = (0, 1 - r)
        p2 = (0, r)
        c1 = (r, r)
        p3 = (2 * r, r)
        p4 = (2 * r, 1 - r)
        c2 = (r, 1 - r)

        x = points_on_line(p1, p2, sp)
        x.extend(points_on_arc(c1, r, 180, 360, sp))
        x.extend(points_on_line(p3, p4, sp))
        x.extend(points_on_arc(c2, r, 0, 180, sp))
        points.append(x)

    elif char == '1':
        r = 0.2
        x = points_on_arc((0, 1), r, 270, 360, sp)
        x.extend(points_on_line((r, 1), (r, 0), sp))
        points.append(x)

    elif char == '2':
        x = points_on_arc((0.25, 0.75), 0.25, 180, 0, sp)
        # Angle between (0, 0), (0.5, 0.75), and center:
        theta1 = math.atan(3/2)
        # Angle between (0, 0), center, and (0.5, 0.75):
        theta2 = math.pi - 2 * theta1
        d = math.sqrt(0.5**2 + 0.75**2)
        r = d * math.sin(theta1) / math.sin(theta2)
        c = (0.5 - r, 0.75)
        x.extend(points_on_arc(c, r, 0, deg(-theta2), sp))
        x.extend(points_on_line((0, 0), (0.5, 0), sp))
        points.append(x)

    elif char == '3':
        x = points_on_arc((0.25, 0.75), 0.25, 180, -90, sp)
        x.extend(points_on_arc((0.25, 0.25), 0.25, 90, -180, sp))
        points.append(x)

    elif char == '4':
        x = points_on_line((0.5, 0), (0.5, 1), sp)
        x.extend(points_on_line((0.5, 1), (0, 1/3), sp))
        x.extend(points_on_line((0, 1/3), (2/3, 1/3), sp))
        points.append(x)

    elif char == '5':
        x = points_on_line((2/3, 1), (0, 1), sp)
        x.extend(points_on_line((0, 1), (0, 2/3), sp))
        x.extend(points_on_line((0, 2/3), (1/3, 2/3), sp))
        x.extend(points_on_arc((1/3, 1/3), 1/3, 90, -180, sp))
        points.append(x)

    elif char == '6':
        x = points_on_arc((2/3, 1/3), 2/3, 90, 180, sp)
        x.extend(points_on_arc((1/3, 1/3), 1/3, -180, 180, sp))
        points.append(x)

    elif char == '7':
        x = points_on_line((0, 1), (2/3, 1), sp)
        # x.extend(points_on_line((2/3, 1), (0, 0), sp))
        cx = 2/3 + 1
        r = math.sqrt(2)
        # theta = 180 - deg(math.acos(4/5))
        theta = 180 - deg(math.acos(1 / r))
        x.extend(points_on_arc((cx, 0), r, theta, 180, sp))
        points.append(x)

    elif char == '8':
        x = points_on_arc((0.25, 0.75), 0.25, -90, 270, sp)
        x.extend(points_on_arc((0.25, 0.25), 0.25, 90, -270, sp))
        points.append(x)

    elif char == '9':
        x = points_on_arc((0, 2/3), 2/3, 270, 360, sp)
        x.extend(points_on_arc((1/3, 2/3), 1/3, 0, 360, sp))
        points.append(x)

    elif char == '.':
        r = 0.05

        points.append(points_on_arc((r, r), r, 0, 360, sp))

    elif char == ',':
        points.append(points_on_line((0.2, 0.1), (0, -0.1), sp))

    elif char == '!':
        r = 0.05

        points.append(points_on_arc((r, r), r, 0, 360, sp))
        points.append(points_on_line((r, 0.3), (r, 1), sp))

    elif char == '?':
        x = points_on_arc((0.25, 0.75), 0.25, 180, -90, sp)
        x.extend(points_on_line((0.25, 0.5), (0.25, 0.3), sp))
        points.append(x)

        r = 0.05
        points.append(points_on_arc((0.25, r), r, 0, 360, sp))

    elif char == ':':
        r = 0.05

        points.append(points_on_arc((r, 0.7), r, 0, 360, sp))
        points.append(points_on_arc((r, r), r, 0, 360, sp))

    elif char == ';':
        r = 0.05

        points.append(points_on_arc((r, 0.7), r, 0, 360, sp))
        points.append(points_on_line((0.2, 0.1), (0, -0.1), sp))

    elif char == "'":
        p1 = (0, 1)
        p2 = (0, 0.9)
        points.append(points_on_line(p1, p2, sp))

    elif char == '"':
        points.append(points_on_line((0, 1), (0, 0.9), sp))
        points.append(points_on_line((0.2, 1), (0.2, 0.9), sp))

    elif char == '/':
        points.append(points_on_line((0, 0), (0.5, 1), sp))

    scale_points(points, h)
    translate_points(points, start[0], start[1])

    return points


def _rel_char_spacing(char: str) -> Tuple[Number, Number]:
    """Get character's left and right spacing relative to line height."""
    spacing = {
        'A': (0.5, 0.5),
        'B': (1, 0.75),
        'C': (0.75, 0.5),
        'D': (1, 0.75),
        'E': (1, 0.5),
        'F': (1, 0.5),
        'G': (0.75, 0.75),
        'H': (1, 1),
        'I': (0.5, 0.5),
        'J': (0.5, 1),
        'K': (1, 0.5),
        'L': (1, 0.5),
        'M': (1, 1),
        'N': (1, 1),
        'O': (0.75, 0.75),
        'P': (1, 0.75),
        'Q': (0.75, 0.75),
        'R': (1, 0.75),
        'S': (0.75, 0.75),
        'T': (0.5, 0.5),
        'U': (1, 1),
        'V': (0.5, 0.5),
        'W': (0.5, 0.5),
        'X': (0.5, 0.5),
        'Y': (0.5, 0.5),
        'Z': (0.5, 0.5),
        'a': (0.5, 1),
        'b': (1, 0.75),
        'c': (0.75, 0.5),
        'd': (0.75, 1),
        'e': (0.75, 0.75),
        'f': (0.5, 0.5),
        'g': (0.75, 1),
        'h': (1, 1),
        'i': (0.5, 0.5),
        'j': (0.25, 0.75),
        'k': (1, 0.5),
        'l': (1, 0.5),
        'm': (1, 1),
        'n': (1, 1),
        'o': (0.75, 0.75),
        'p': (1, 0.75),
        'q': (0.75, 1),
        'r': (1, 0.5),
        's': (0.75, 0.75),
        't': (0.5, 0.5),
        'u': (1, 1),
        'v': (0.5, 0.5),
        'w': (0.5, 0.5),
        'x': (0.5, 0.5),
        'y': (0.5, 0.5),
        'z': (0.5, 0.5),
        '0': (0.75, 0.75),
        '1': (0.5, 1),
        '2': (0.5, 0.75),
        '3': (0.5, 0.75),
        '4': (0.5, 0.5),
        '5': (1, 0.75),
        '6': (0.75, 0.75),
        '7': (0.5, 0.5),
        '8': (0.75, 0.75),
        '9': (0.75, 0.75),
        '.': (0.5, 0.5),
        ',': (0.5, 0.5),
        '!': (0.75, 0.75),
        '?': (0.5, 0.75),
        ':': (0.5, 0.5),
        ';': (0.5, 0.5),
        "'": (0.5, 0.5),
        '"': (0.5, 0.5),
        '/': (0.5, 0.5),
        ' ': (2, 2)
    }
    if char in spacing:
        return spacing[char]
    else:
        print(char, "isn't currently drawable.")
        return (0.5, 0.5)


def text_points(text: str, height: Number, pt_spacing: Number, char_spacing:
                Number = 0.1, grouping: str =
                'points') -> Union[List[Point], List[List[Point]]]:
    """Generate points that spell out text.

    Text starts at (0, 0) and should be repositioned.

    Args:
        text: The text.
        height: Line height.
        pt_spacing: Approximate distance between adjacent points.
        char_spacing: Size of the largest space on either side of each
          character relative to line height.  This space is shrunk for
          certain characters depending on shape.
        grouping: 'points' to return list of points, 'strokes' to
          group by stroke.

    Returns:
        Either a list of points or a list of lists of points in which
        each list of points corresponds to a pen stroke (i.e. what can
        be drawn without lifting the pin).

    """
    strokes = []
    x = 0
    for char in text:
        left_space, right_space = _rel_char_spacing(char)

        x += left_space * char_spacing * height

        char_strokes = char_points(char, (x, 0), height, pt_spacing)
        strokes.extend(char_strokes)
        char_pts = [point for stroke in char_strokes for point in stroke]
        x += horizontal_range(char_pts)

        x += right_space * char_spacing * height

    if grouping == 'points':
        return [point for stroke in strokes for point in stroke]
    elif grouping == 'strokes':
        return strokes


def splatter_text(text: str, height: Number, spread: Number, density:
                  Number, min_size: Number, max_size: Number, color:
                  Color) -> List[dict]:
    """Generate text with paint splatter appearance.

    Args:
        text: The text.
        height: The line height.
        spread: Standard deviation of point jittering.
        density: Number of dots per pixel.
        min_size: The smallest dot radius.
        max_size: The largest dot radius.
        color: A fill Color.

    Returns:
        A list of circle shapes (in random order).

    """
    spacing = 1 / density
    points = text_points(text, height, spacing, 0.15)
    jitter_points(points, spread)
    size = shuffled(geom_seq(max_size, min_size, len(points)))
    x = [circle(c=p, r=size[i], fill=color) for i, p in enumerate(points)]
    return shuffled(x)


def double_dots_text(text: str, height: Number, top_color: Color =
                     'white', bottom_color: Color =
                     'black') -> List[List[dict]]:
    """Generate text with one splatter color over another.

    Args:
        text: The text.
        height: The line height.
        top_color: The color for top (inner) splatters.
        bottom_color: The color for bottom (outer) splatters.

    Returns:
        A list of two lists of circle shapes (inner lists are
        randomized).

    """
    x = splatter_text(text, height, spread=height/10,
                      density=500/height, min_size=height/100,
                      max_size=height/15, color=bottom_color)
    y = splatter_text(text, height, spread=height/30,
                      density=100/height, min_size=height/100,
                      max_size=height/25, color=top_color)
    return [x, y]


def hazy_text(text: str, height: Number, spread: Number, density:
              Number, min_size: Number, max_size: Number, color:
              Color) -> List[dict]:
    """Generate text with hazy dots effect.

    Similar to splatter text but dot size is inversely proportional to
    square root of deviation, and points are uniformly jittered.

    Args:
        text: The text.
        height: The line height.
        spread: Standard deviation of point jittering.
        density: Number of dots per pixel.
        min_size: The smallest dot radius.
        max_size: The largest dot radius.
        color: A fill color or function.

    Returns:
        A list of circle shapes (in random order).

    """
    spacing = 1 / density
    points = text_points(text, height, spacing, 0.15)
    angles = np.random.uniform(0, 2 * math.pi, len(points))
    dists = np.random.uniform(0, spread, len(points))
    sqrt_dists = [math.sqrt(d) for d in dists]
    min_sqrt_dist = min(sqrt_dists)
    max_sqrt_dist = max(sqrt_dists)
    rel_sqrt_dists = [(d - min_sqrt_dist) / (max_sqrt_dist - min_sqrt_dist)
                      for d in sqrt_dists]
    sizes = [min_size + (1 - d) * (max_size - min_size) for d in
             rel_sqrt_dists]
    points = [endpoint(p, angles[i], dists[i]) for i, p in enumerate(points)]
    x = [circle(c=p, r=sizes[i], fill=color) for i, p in enumerate(points)]
    return shuffled(x)


def squiggle_text(text: str, height: Number, spread: Number, density:
                  Number) -> List[dict]:
    """Generate squiggly line text.

    Args:
        text: The text.
        height: The line height.
        spread: Maximum deviation of point jittering.
        density: Number of spline points per pixel.

    Returns:
        A list of splines.

    """
    spacing = 1 / density
    strokes = text_points(text, height, pt_spacing=spacing,
                          char_spacing=0.2, grouping='strokes')
    for stroke in strokes:
        jitter_points(stroke, spread)
    splines = [spline(points=stroke, fill='none', stroke='black') for stroke in strokes]
    return splines


def caption(text: str, anchor: Point, align: str = 'right', color:
            Color = '#aaa', font_size: Number = 14) -> dict:
    """Generate a caption.

    Args:
        text: The text.
        anchor: The reference point.
        align: The alignment to reference point: 'left', 'center', or 'right'.
        color: The text fill color.
        font_size: The font size.

    Returns:
        A text shape.

    """
    t = dict(type='text', text=text, x=anchor[0], y=anchor[1],
             align=align, font_size=font_size)
    set_style(t, 'fill', color)
    return t
