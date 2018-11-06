import subprocess
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
import algoraphics as ag

os.chdir(script_dir)

w = 800
h = 800

######################################################################
# Fixed-width filaments
######################################################################

dirs = [ag.Param(d, delta=ag.Uniform(min=-20, max=20))
        for d in range(360)[::10]]
width = ag.Uniform(min=8, max=12)
length = ag.Uniform(min=8, max=12)
x = [ag.filament(start=(w / 2., h / 2.), direction=d, width=width,
                 seg_length=length, n_segments=40) for d in dirs]
y = [ag.filament(start=(w / 2., h / 2.), direction=d, width=width,
                 seg_length=length, n_segments=30) for d in dirs]

ag.set_style(x, 'fill', ag.Color(hsl=(ag.Uniform(min=0.6, max=0.75), 1, 0.5)))
ag.set_style(y, 'fill', ag.Color(hsl=(ag.Uniform(min=0, max=0.15), 1, 0.5)))

ag.write_SVG([x, y], w, h, 'svg/filaments1.svg')
subprocess.run(['convert', 'svg/filaments1.svg', 'png/filaments1.png'])


######################################################################
# Fixed-width filaments with smooth curls
######################################################################

direc = ag.Param(90, delta=ag.Param(0, min=-20, max=20,
                                    delta=ag.Uniform(min=-3, max=3)))
# direc = ag.Param(90, delta=ag.Param(min=-20, max=20))
x = [ag.filament(start=(z, -10), direction=direc, width=10,
                 seg_length=10, n_segments=80) for z in range(w)[::50]]
y = [ag.filament(start=(z, -10), direction=direc, width=10,
                 seg_length=10, n_segments=60) for z in range(w)[::50]]

ag.set_style(x, 'fill', ag.Color(hsl=(0.33, 1, ag.Uniform(min=0.15, max=0.35))))
ag.set_style(y, 'fill', ag.Color(hsl=(0.33, 1, ag.Uniform(min=0.35, max=0.55))))

ag.write_SVG([x, y], w, h, "svg/filaments2.svg")
subprocess.run(['convert', 'svg/filaments2.svg', 'png/filaments2.png'])


######################################################################
# Tapered filaments (tentacles)
######################################################################

dirs = [ag.Param(d, delta=ag.Uniform(min=-30, max=30))
        for d in range(360)[::10]]
n_seg = 50
width = ag.Param(10, delta=-10 / n_seg)
length = ag.Param(10, delta=-5 / n_seg)
x = [ag.filament(start=(w / 2., h / 2.), direction=d, width=width,
                 seg_length=length, n_segments=n_seg) for d in dirs]
n_seg = 40
width = ag.Param(10, delta=-10 / n_seg)
length = ag.Param(10, delta=-5 / n_seg)
y = [ag.filament(start=(w / 2., h / 2.), direction=d, width=width,
                 seg_length=length, n_segments=n_seg) for d in dirs]

ag.set_style(x, 'fill', ag.Color(hsl=(ag.Uniform(min=0.6, max=0.75), 1, 0.5)))
ag.set_style(y, 'fill', ag.Color(hsl=(ag.Uniform(min=0, max=0.15), 1, 0.5)))

ag.write_SVG([x, y], w, h, "svg/filaments3.svg")
subprocess.run(['convert', 'svg/filaments3.svg', 'png/filaments3.png'])


######################################################################
# Tapered filaments (tentacles) with smooth curls
######################################################################

direc = ag.Param(90, delta=ag.Param(0, min=-20, max=20,
                                    delta=ag.Uniform(min=-5, max=5)))
n_seg = 80
width = ag.Param(20, delta=-20 / n_seg)
length = ag.Param(16, delta=-8 / n_seg)
x = [ag.filament(start=(z, -10), direction=direc, width=width,
                 seg_length=length, n_segments=n_seg) for z in range(w)[::50]]
n_seg = 60
width = ag.Param(20, delta=-20 / n_seg)
length = ag.Param(16, delta=-8 / n_seg)
y = [ag.filament(start=(z, -10), direction=direc, width=width,
                 seg_length=length, n_segments=n_seg) for z in range(w)[::50]]

ag.set_style(x, 'fill', ag.Color(hsl=(0.33, 1, ag.Uniform(min=0.15, max=0.35))))
ag.set_style(y, 'fill', ag.Color(hsl=(0.33, 1, ag.Uniform(min=0.35, max=0.55))))

ag.write_SVG([x, y], w, h, "svg/filaments4.svg")
subprocess.run(['convert', 'svg/filaments4.svg', 'png/filaments4.png'])
