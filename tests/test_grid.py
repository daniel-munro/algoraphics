import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
import algoraphics as ag

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Straight-line maze-like pattern
######################################################################

outline = ag.rectangle(bounds=(0, w, 0, h))
x = ag.fill_maze(outline, spacing=20,
                 style=ag.Maze_Style_Straight(rel_thickness=0.2))
ag.set_style(x['members'], 'fill', 'blue')

ag.write_SVG(x, w, h, 'svg/grid1.svg')
ag.to_PNG('svg/grid1.svg', 'png/grid1.png')


######################################################################
# Jagged-width maze-like pattern
######################################################################

outline = ag.rectangle(bounds=(0, w, 0, h))
x = ag.fill_maze(outline, spacing=20,
                 style=ag.Maze_Style_Jagged(min_w=0.2, max_w=0.8))
ag.set_style(x['members'], 'fill', 'blue')

ag.write_SVG(x, w, h, 'svg/grid2.svg')
ag.to_PNG('svg/grid2.svg', 'png/grid2.png')


######################################################################
# Maze-like pipes
######################################################################

outline = ag.rectangle(bounds=(0, w, 0, h))
x = ag.fill_maze(outline, spacing=20,
                 style=ag.Maze_Style_Pipes(rel_thickness=0.6))
ag.set_style(x['members'], 'fill', 'blue')

ag.write_SVG(x, w, h, 'svg/grid3.svg')
ag.to_PNG('svg/grid3.svg', 'png/grid3.png')


######################################################################
# Maze-like curvy pipes
######################################################################

outline = ag.rectangle(bounds=(0, w, 0, h))
x = ag.fill_maze(outline, spacing=20,
                 style=ag.Maze_Style_Round(rel_thickness=0.3),
                 rotation=45)
ag.set_style(x['members'], 'fill', 'blue')

ag.write_SVG(x, w, h, 'svg/grid4.svg')
ag.to_PNG('svg/grid4.svg', 'png/grid4.png')
