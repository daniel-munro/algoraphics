import subprocess
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
from algoraphics.ripples import ripple_canvas
from algoraphics.main import set_style
from algoraphics.geom import points_on_arc
from algoraphics.svg import write_SVG

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Object-avoiding ripples
######################################################################

circ = points_on_arc(center=(200, 200), radius=100, theta_start=0,
                     theta_end=360, spacing=10)
x = ripple_canvas(w, h, spacing=10, existing_pts=circ)

write_SVG(x, w, h, 'svg/ripples1.svg')
subprocess.run(['convert', 'svg/ripples1.svg', 'png/ripples1.png'])


######################################################################
# More irregular ripples
######################################################################

trans_probs = dict(s=dict(x=1),
                   r=dict(r=0.9, l=0.05, x=0.05),
                   l=dict(l=0.9, r=0.05, x=0.05),
                   x=dict(r=0.5, l=0.5))
circ = points_on_arc(center=(200, 200), radius=100, theta_start=0,
                     theta_end=360, spacing=10)
x = ripple_canvas(w, h, spacing=10, trans_probs=trans_probs,
                  existing_pts=circ)

write_SVG(x, w, h, 'svg/ripples2.svg')
subprocess.run(['convert', 'svg/ripples2.svg', 'png/ripples2.png'])
