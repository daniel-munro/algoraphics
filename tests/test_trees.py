import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
import algoraphics as ag

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Trees branching from a point
######################################################################

x = [ag.tree((200, 200), direction=d,
             branch_length=ag.Uniform(min=8, max=20),
             theta=ag.Uniform(min=15, max=20),
             p=ag.Param(1, delta=-0.08))
     for d in range(360)[::20]]
ag.set_style(x, 'stroke', ag.Color(hue=ag.Normal(0.12, stdev=0.05),
                                   sat=ag.Uniform(0.4, 0.7),
                                   li=0.3))
ag.write_SVG(x, w, h, 'svg/trees1.svg')
ag.to_PNG('svg/trees1.svg', 'png/trees1.png')
