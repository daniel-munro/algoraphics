import subprocess
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
from algoraphics.trees import tree
from algoraphics.main import set_style
from algoraphics.color import rand_col_from_ranges
from algoraphics.svg import write_SVG

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Trees branching from a point
######################################################################

x = [tree((200, 200), direction=d, l_min=8, l_max=20, theta=15,
          p=0.99, p_delta=0.1) for d in range(360)[::20]]
set_style(x, 'stroke', lambda: rand_col_from_ranges(150, range(100, 150), 100))
write_SVG(x, w, h, 'svg/trees1.svg')
subprocess.run(['convert', 'svg/trees1.svg', 'png/trees1.png'])
