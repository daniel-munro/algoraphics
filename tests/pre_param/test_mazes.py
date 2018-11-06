import subprocess
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
from algoraphics.mazes import fill_maze, Maze_Style_Straight, Maze_Style_Jagged
from algoraphics.mazes import Maze_Style_Pipes, Maze_Style_Round
from algoraphics.main import set_style, background
from algoraphics.svg import write_SVG

os.chdir(script_dir)

w = 400
h = 400

outline = background(None, w, h)

######################################################################
# Straight-line maze-like pattern
######################################################################

x = fill_maze(outline, spacing=20,
              style=Maze_Style_Straight(rel_thickness=0.2))
set_style(x['members'], 'fill', 'blue')
write_SVG(x, w, h, 'svg/mazes1.svg')
subprocess.run(['convert', 'svg/mazes1.svg', 'png/mazes1.png'])


######################################################################
# Jagged-width maze-like pattern
######################################################################

x = fill_maze(outline, spacing=20,
              style=Maze_Style_Jagged(min_w=0.2, max_w=0.8))
set_style(x['members'], 'fill', 'blue')
write_SVG(x, w, h, 'svg/mazes2.svg')
subprocess.run(['convert', 'svg/mazes2.svg', 'png/mazes2.png'])


######################################################################
# Maze-like pipes
######################################################################

x = fill_maze(outline, spacing=20, style=Maze_Style_Pipes(rel_thickness=0.6))
set_style(x['members'], 'fill', 'blue')
write_SVG(x, w, h, 'svg/mazes3.svg')
subprocess.run(['convert', 'svg/mazes3.svg', 'png/mazes3.png'])


######################################################################
# Maze-like curvy pipes
######################################################################

x = fill_maze(outline, spacing=20, style=Maze_Style_Round(rel_thickness=0.3),
              rotation=45)
set_style(x['members'], 'fill', 'blue')
write_SVG(x, w, h, 'svg/mazes4.svg')
subprocess.run(['convert', 'svg/mazes4.svg', 'png/mazes4.png'])
