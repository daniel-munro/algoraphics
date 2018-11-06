import subprocess
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
from algoraphics.space_filling import fill_region, filament_fill
from algoraphics.main import set_style
from algoraphics.color import rand_col_from_ranges
from algoraphics.textures import add_shadows
from algoraphics.paths import circle
from algoraphics.svg import write_SVG

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Filament fill
######################################################################

col = lambda: rand_col_from_ranges(255, range(50, 200), 50)
outline = circle(c=(200, 200), r=100)
filfun = filament_fill(col, width=15, l_min=7, l_max=20)
x = fill_region(outline, filfun)
add_shadows(x['members'])

write_SVG(x, w, h, 'svg/space_filling1.svg')
subprocess.run(['convert', 'svg/space_filling1.svg',
                'png/space_filling1.png'])
