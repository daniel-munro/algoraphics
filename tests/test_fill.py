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

ag.write_SVG(x, w, h, 'svg/fill1.svg')
ag.to_PNG('svg/fill1.svg', 'png/fill1.png')


######################################################################
# Wrapping paper-style object tiling
######################################################################


def doodle1_fun():
    d = ag.circle(c=(0.5, 0.5), r=0.45)
    ag.set_style(d, 'fill', 'green')
    return d


def doodle2_fun():
    d = [ag.circle(c=(0.5, 0.5), r=0.45),
         ag.circle(c=(1, 0.5), r=0.45),
         ag.circle(c=(1.5, 0.5), r=0.45)]
    ag.set_style(d, 'fill', 'red')
    return d


def doodle3_fun():
    d = [ag.rectangle(start=(0.2, 1.2), w=2.6, h=0.6),
         ag.rectangle(start=(1.2, 0.2), w=0.6, h=1.6)]
    ag.set_style(d, 'fill', 'blue')
    return d


doodle1 = ag.Doodle(doodle1_fun, footprint=[[True]])
doodle2 = ag.Doodle(doodle2_fun, footprint=[[True, True]])
doodle3 = ag.Doodle(doodle3_fun, footprint=[[True, True, True],
                                            [False, True, False]])
doodles = [doodle1, doodle2, doodle3]

outline = ag.circle(c=(200, 200), r=180)

x = ag.fill_wrapping_paper(outline, 30, doodles, rotate=True)

ag.write_SVG(x, w, h, 'svg/fill2.svg')
ag.to_PNG('svg/fill2.svg', 'png/fill2.png')
