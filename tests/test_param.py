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
# Circles 1
######################################################################

w, h = 400, 200
center = (ag.Uniform(10, w - 10), ag.Uniform(10, h - 10))
radius = ag.Uniform(1, 10)
color = ag.Color(hue=ag.Uniform(0.4, 0.6), sat=0.9, li=0.5)
x = [ag.circle(center, radius) for i in range(100)]
ag.set_style(x, 'fill', color)

ag.write_SVG(x, w, h, 'svg/param1.svg')
subprocess.run(['convert', 'svg/param1.svg', 'png/param1.png'])


######################################################################
# Circles 2
######################################################################

w, h = 400, 200
center = (ag.Param([100, 300]), 100)
radius = ag.Param(100, delta=-1)
color = ag.Color(hue=0.8, sat=0.9, li=ag.Uniform(0, 1))
x = [ag.circle(center, radius) for i in range(100)]
ag.set_style(x, 'fill', color)

ag.write_SVG(x, w, h, 'svg/param2.svg')
subprocess.run(['convert', 'svg/param2.svg', 'png/param2.png'])


######################################################################
# Circles 3
######################################################################

w, h = 400, 200
center = (ag.Param(0, delta=4), ag.Uniform(0, h))
radius = ag.Uniform(5, 30)
color = ag.Color(hue=ag.Param(0, delta=0.005), sat=0.9, li=0.5)
x = [ag.circle(center, radius) for i in range(100)]
ag.set_style(x, 'fill', color)

ag.write_SVG(x, w, h, 'svg/param3.svg')
subprocess.run(['convert', 'svg/param3.svg', 'png/param3.png'])
