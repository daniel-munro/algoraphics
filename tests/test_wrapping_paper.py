import subprocess
import os
import sys
import numpy as np
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
from algoraphics.wrapping_paper import fill_wrapping_paper
from algoraphics.paths import rectangle, circle
from algoraphics.main import set_style
from algoraphics.svg import write_SVG

os.chdir(script_dir)


def doodle1(footprint=False):
    if footprint:
        return np.array([[True]])
    else:
        d = circle(c=(0.5, 0.5), r=0.45)
        set_style(d, 'fill', 'green')
        return d


def doodle2(footprint=False):
    if footprint:
        return np.array([[True, True]])
    else:
        d = [circle(c=(0.5, 0.5), r=0.45),
             circle(c=(1, 0.5), r=0.45),
             circle(c=(1.5, 0.5), r=0.45)]
        set_style(d, 'fill', 'red')
        return d


def doodle3(footprint=False):
    if footprint:
        # TODO: Maybe footprint should be the first, not second:
        # return np.array([[True, True, True],
        #                  [False, True, False]])
        return np.array([[False, True, False],
                         [True, True, True]])
    else:
        d = [rectangle(start=(0.2, 1.2), w=2.6, h=0.6),
             rectangle(start=(1.2, 0.2), w=0.6, h=1.6)]
        set_style(d, 'fill', 'blue')
        return d


w = 400
h = 400

######################################################################
# Wrapping paper-style object tiling
######################################################################

doodles = [doodle1, doodle2, doodle3]

outline = circle(c=(200, 200), r=180)

x = fill_wrapping_paper(outline, 30, doodles, rotate=True)

write_SVG(x, w, h, 'svg/wrapping_paper1.svg')
subprocess.run(['convert', 'svg/wrapping_paper1.svg',
                'png/wrapping_paper.png'])
