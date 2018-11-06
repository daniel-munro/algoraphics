import subprocess
import os
import sys
import numpy as np
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
from algoraphics.text import splatter_text, double_dots_text, hazy_text
from algoraphics.text import squiggle_text, caption
from algoraphics.color import rand_col_from_ranges
from algoraphics.main import set_style, reposition
from algoraphics.svg import write_SVG

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Splatter text
######################################################################

x = []

col = lambda: rand_col_from_ranges(255, range(50, 200), 50)
y = splatter_text('ABCDEFG', height=50, spread=2, density=2,
                  min_size=1, max_size=3, fill=col)
reposition(y, (w / 2., h - 50), 'center', 'top')
x.append(y)

y = splatter_text('HIJKLM', height=50, spread=2, density=2,
                  min_size=1, max_size=3, fill=col)
reposition(y, (w / 2., h - 150), 'center', 'top')
x.append(y)

write_SVG(x, w, h, 'svg/text1.svg')
subprocess.run(['convert', 'svg/text1.svg', 'png/text1.png'])


######################################################################
# Double dots text
######################################################################

x = []

y = double_dots_text('NOPQRST', height=40)
reposition(y, (w / 2., h - 50), 'center', 'top')
x.append(y)

y = double_dots_text('UVWXYZ', height=40, top_color='#FF8888',
                     bottom_color='#555555')
reposition(y, (w / 2., h - 150), 'center', 'top')
x.append(y)

write_SVG(x, w, h, 'svg/text2.svg')
subprocess.run(['convert', 'svg/text2.svg', 'png/text2.png'])


######################################################################
# Hazy text
######################################################################

x = []

y = hazy_text('abcdefg', height=50, spread=10, density=3, min_size=0.5,
              max_size=2, fill='green')
reposition(y, (w / 2., h - 100), 'center', 'top')
x.append(y)

y = hazy_text('hijklm', height=50, spread=10, density=3, min_size=0.5,
              max_size=2, fill='green')
reposition(y, (w / 2., h - 250), 'center', 'top')
x.append(y)

write_SVG(x, w, h, 'svg/text3.svg')
subprocess.run(['convert', 'svg/text3.svg', 'png/text3.png'])


######################################################################
# Squiggle text
######################################################################

x = []

y = squiggle_text('nopqrst', height=60, spread=10, density=1)
reposition(y, (w / 2., h - 100), 'center', 'top')
x.append(y)

y = squiggle_text('uvwxyz', height=60, spread=10, density=1)
reposition(y, (w / 2., h - 250), 'center', 'top')
x.append(y)

write_SVG(x, w, h, 'svg/text4.svg')
subprocess.run(['convert', 'svg/text4.svg', 'png/text4.png'])


######################################################################
# Caption (SVG text)
######################################################################

x = caption("SVG text.", x=w-20, y=20)
write_SVG(x, w, h, 'svg/text5.svg')
subprocess.run(['convert', 'svg/text5.svg', 'png/text5.png'])
