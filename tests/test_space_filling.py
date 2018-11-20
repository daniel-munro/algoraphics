import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
import algoraphics as ag

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Filament fill
######################################################################

color = ag.Color(hsl=(ag.Uniform(min=0, max=0.15), 1, 0.5))
outline = ag.circle(c=(200, 200), r=100)
dir_delta = ag.Uniform(min=-20, max=20)
width = ag.Uniform(min=8, max=12)
length = ag.Uniform(min=8, max=12)
filfun = ag.filament_fill(direction_delta=dir_delta, width=width,
                          seg_length=length, color=color)
x = ag.fill_region(outline, filfun)
ag.add_shadows(x['members'])

ag.write_SVG(x, w, h, 'svg/space_filling1.svg')
ag.to_PNG('svg/space_filling1.svg', 'png/space_filling1.png')
