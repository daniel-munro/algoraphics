import subprocess
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
import algoraphics as ag

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Object-avoiding ripples
######################################################################

circ = ag.points_on_arc(center=(200, 200), radius=100, theta_start=0,
                        theta_end=360, spacing=10)
x = ag.ripple_canvas(w, h, spacing=10, existing_pts=circ)

ag.write_SVG(x, w, h, 'svg/ripples1.svg')
subprocess.run(['convert', 'svg/ripples1.svg', 'png/ripples1.png'])


######################################################################
# More irregular ripples
######################################################################

trans_probs = dict(S=dict(X=1),
                   R=dict(R=0.9, L=0.05, X=0.05),
                   L=dict(L=0.9, R=0.05, X=0.05),
                   X=dict(R=0.5, L=0.5))
circ = ag.points_on_arc(center=(200, 200), radius=100, theta_start=0,
                        theta_end=360, spacing=10)
x = ag.ripple_canvas(w, h, spacing=10, trans_probs=trans_probs,
                     existing_pts=circ)

ag.write_SVG(x, w, h, 'svg/ripples2.svg')
subprocess.run(['convert', 'svg/ripples2.svg', 'png/ripples2.png'])
