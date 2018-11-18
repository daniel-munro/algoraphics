import subprocess
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
from algoraphics.textures import add_shadows, billow_region, add_paper_texture
from algoraphics.textures import tear_paper_rect
from algoraphics.paths import rectangle, circle
from algoraphics.main import set_style
from algoraphics.color import rand_col_from_ranges
from algoraphics.svg import write_SVG

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Shadows
######################################################################

d = [dict(command='M', to=(50, 50)),
     dict(command='L', to=(50, 350)),
     dict(command='L', to=(350, 50)),
     dict(command='L', to=(50, 50)),
     dict(command='M', to=(70, 70)),
     dict(command='L', to=(320, 70)),
     dict(command='L', to=(70, 320)),
     dict(command='L', to=(70, 70))]
path = dict(type='path', d=d)
set_style(path, 'fill', "#55FF55")

centers = [(300, 250), (250, 300)]
circles = [circle(c=c, r=50) for c in centers]
set_style(circles[0], 'fill', "#FFDDDD")
set_style(circles[1], 'fill', "#DDDDFF")

x = [path, circles]
# Note that add_shadows adds shadows to the immediate list elements as
# wholes, meaning the top circle should not project a shadow onto the
# one behind it.
add_shadows(x, stdev=20, darkness=0.5)
write_SVG(x, w, h, 'svg/textures1.svg')
subprocess.run(['convert', 'svg/textures1.svg', 'png/textures1.png'])


######################################################################
# Billowing
######################################################################

outline = circle(c=(120, 120), r=100)
colors = [(139, 0, 0), (255, 140, 0), (255, 215, 0), (0, 100, 0)]
x = billow_region(outline, colors, scale=200, gradient_mode='rgb')

outline = circle(c=(280, 280), r=100)
colors = [(139, 0, 0), (0, 0, 100)]
y = billow_region(outline, colors, scale=400, gradient_mode='hsl')

write_SVG([x, y], w, h, 'svg/textures2.svg')
subprocess.run(['convert', 'svg/textures2.svg', 'png/textures2.png'])


######################################################################
# Paper
######################################################################

x = [rectangle(start=(50, 50), w=300, h=300),
     circle(c=(200, 200), r=150)]
set_style(x[0], 'fill', 'green')
set_style(x[1], 'fill', '#FFCCCC')
add_paper_texture(x)
x = tear_paper_rect(x, (60, 340, 60, 340))

write_SVG(x, w, h, 'svg/textures3.svg')
subprocess.run(['convert', 'svg/textures3.svg', 'png/textures3.png'])