import subprocess
import os
import sys
import numpy as np
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
from algoraphics.paths import wave
from algoraphics.color import hsl_to_rgb
from algoraphics.main import set_style
from algoraphics.svg import write_SVG

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Waves
######################################################################

n_waves = 100
x = []
for d in (1 + np.arange(n_waves)) / n_waves:
    wav = wave(start=(200, 200), direction=d * 360, width=d * 20,
               period=1 + d * 30, length=1 + d * 180)
    set_style(wav, 'stroke', hsl_to_rgb((d, 1, 0.5)))
    set_style(wav, 'stroke_width', d * 2)
    x.append(wav)

write_SVG(x, w, h, 'svg/paths1.svg')
subprocess.run(['convert', 'svg/paths1.svg', 'png/paths1.png'])
