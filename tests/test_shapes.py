import os
import sys
import numpy as np
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
import algoraphics as ag

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Waves
######################################################################

# n_waves = 100
# x = []
# for d in (1 + np.arange(n_waves)) / n_waves:
#     wav = ag.wave(start=(200, 200), direction=d * 360, width=d * 20,
#                   period=1 + d * 30, length=1 + d * 180)
#     ag.set_style(wav, 'stroke', (d, 1, 0.5))
#     ag.set_style(wav, 'stroke-width', d * 2)
#     x.append(wav)

# ag.write_SVG(x, w, h, 'svg/shapes1.svg')
# ag.to_PNG('svg/shapes1.svg', 'png/shapes1.png')


######################################################################
# Wobble (make edges a little messy)
######################################################################

x = []
x.append(ag.circle(c=(100, 100), r=80))
x.append(ag.line(p1=(200, 30), p2=(250, 170)))
x.append(ag.line(points=[(300, 30), (330, 170), (350, 90), (370, 160)]))
x.append(ag.polygon(points=[(30, 230), (30, 370), (170, 230), (170, 370)]))
x.append(ag.wave(start=(230, 230), direction=45,
                 period=ag.Param(20, delta=0.1), length=200))

# TODO: test semicircle path.

ag.wobble(x)

ag.write_SVG(x, w, h, 'svg/shapes2.svg')
ag.to_PNG('svg/shapes2.svg', 'png/shapes2.png')
