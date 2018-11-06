import subprocess
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
from algoraphics.paint import blow_paint_area, blow_paint_line, blow_paint_spot
from algoraphics.main import set_style
from algoraphics.svg import write_SVG

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Blow-paint effects (polygon, line, and spot)
######################################################################

pts1 = [(50, 50), (50, 100), (100, 70), (150, 130), (200, 60)]
x1 = blow_paint_area(pts1)

pts2 = [(250, 50), (350, 50), (300, 200)]
x2 = blow_paint_area(pts2, spacing=20, length=20, len_dev=0.4, width=8)
set_style(x2, 'fill', 'orange')

pts3 = [(50, 300), (100, 350), (200, 250), (300, 300)]
y = blow_paint_line(pts3, line_width=8, spacing=15, length=30,
                    len_dev=0.4, width=6)
set_style(y, 'fill', 'red')

z = blow_paint_spot((350, 350), length=20)
set_style(z, 'stroke', 'blue')

write_SVG([x1, x2, y, z], w, h, 'svg/paint1.svg')
subprocess.run(['convert', 'svg/paint1.svg', 'png/paint1.png'])
