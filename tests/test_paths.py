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

n_waves = 100
x = []
for d in (1 + np.arange(n_waves)) / n_waves:
    wav = ag.wave(start=(200, 200), direction=d * 360, width=d * 20,
                  period=1 + d * 30, length=1 + d * 180)
    ag.set_style(wav, 'stroke', (d, 1, 0.5))
    ag.set_style(wav, 'stroke-width', d * 2)
    x.append(wav)

ag.write_SVG(x, w, h, 'svg/paths1.svg')
ag.to_PNG('svg/paths1.svg', 'png/paths1.png')
