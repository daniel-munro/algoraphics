import subprocess
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
from algoraphics.filaments import filament, tapered_filament
from algoraphics.main import set_style
from algoraphics.color import rand_col_from_ranges
from algoraphics.svg import write_SVG

os.chdir(script_dir)

w = 800
h = 800

######################################################################
# Fixed-width filaments
######################################################################

x = [filament(start=(w / 2., h / 2.), direction=d, width=10, l_min=5,
              l_max=8, segments=50) for d in range(360)[::10]]
y = [filament(start=(w / 2., h / 2.), direction=d, width=10, l_min=5,
              l_max=9, segments=40) for d in range(360)[::10]]

set_style(x, 'fill', lambda: rand_col_from_ranges(range(50, 150),
                                                  range(50, 150), 255))
set_style(y, 'fill', lambda: rand_col_from_ranges(255, range(50, 200),
                                                  50))

write_SVG([x, y], w, h, 'svg/filaments1.svg')
subprocess.run(['convert', 'svg/filaments1.svg', 'png/filaments1.png'])


######################################################################
# Fixed-width filaments with smooth curls
######################################################################

x = [filament(start=(z, -10), direction=90, width=10, l_min=7,
              l_max=9, segments=80, l_max_step=0.2) for z in range(w)[::50]]
y = [filament(start=(z, -10), direction=90, width=10, l_min=7,
              l_max=9, segments=60, l_max_step=0.2) for z in range(w)[::50]]

set_style(x, 'fill', lambda: rand_col_from_ranges(50, range(50, 150), 50))
set_style(y, 'fill', lambda: rand_col_from_ranges(50, range(150, 255), 50))

write_SVG([x, y], w, h, "svg/filaments2.svg")
subprocess.run(['convert', 'svg/filaments2.svg', 'png/filaments2.png'])


######################################################################
# Tapered filaments (tentacles)
######################################################################

x = [tapered_filament(start=(w / 2., h / 2.), direction=d, width=10,
                      l_min=10, l_max=16, segments=50) for d in
     range(360)[::10]]
y = [tapered_filament(start=(w / 2., h / 2.), direction=d, width=10,
                      l_min=10, l_max=18, segments=40) for d in
     range(360)[::10]]

set_style(x, 'fill', lambda: rand_col_from_ranges(range(50, 150),
                                                  range(50, 150), 255))
set_style(y, 'fill', lambda: rand_col_from_ranges(255, range(50, 200),
                                                  50))

write_SVG([x, y], w, h, "svg/filaments3.svg")
subprocess.run(['convert', 'svg/filaments3.svg', 'png/filaments3.png'])


######################################################################
# Tapered filaments (tentacles) with smooth curls
######################################################################

x = [tapered_filament(start=(z, -10), direction=90, width=10,
                      l_min=12, l_max=18, segments=80, l_max_step=2) for z
     in range(w)[::50]]
y = [tapered_filament(start=(z, -10), direction=90, width=10,
                      l_min=12, l_max=18, segments=60, l_max_step=2) for z
     in range(w)[::50]]

set_style(x, 'fill', lambda: rand_col_from_ranges(50, range(50, 150), 50))
set_style(y, 'fill', lambda: rand_col_from_ranges(50, range(150, 255), 50))

write_SVG([x, y], w, h, "svg/filaments4.svg")
subprocess.run(['convert', 'svg/filaments4.svg', 'png/filaments4.png'])
