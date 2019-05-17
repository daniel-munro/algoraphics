import os
import algoraphics as ag

os.chdir(os.path.dirname(os.path.abspath(__file__)))

w, h = 400, 400
c = ag.Canvas(w, h)

###################################
# Straight-line maze-like pattern #
###################################

outline = ag.rectangle(bounds=(0, 0, w, h))
x = ag.fill_maze(outline, spacing=20,
                 style=ag.Maze_Style_Straight(rel_thickness=0.2))
ag.set_style(x['members'], 'fill', 'blue')

c.add(x)
c.png("png/mazes1.png")


##################################
# Jagged-width maze-like pattern #
##################################

outline = ag.rectangle(bounds=(0, 0, w, h))
x = ag.fill_maze(outline, spacing=20,
                 style=ag.Maze_Style_Jagged(min_w=0.2, max_w=0.8))
ag.set_style(x['members'], 'fill', 'blue')

c.new(x)
c.png("png/mazes2.png")


###################
# Maze-like pipes #
###################

outline = ag.rectangle(bounds=(0, 0, w, h))
x = ag.fill_maze(outline, spacing=20,
                 style=ag.Maze_Style_Pipes(rel_thickness=0.6))
ag.set_style(x['members'], 'fill', 'blue')

c.new(x)
c.png("png/mazes3.png")


#########################
# Maze-like curvy pipes #
#########################

outline = ag.rectangle(bounds=(0, 0, w, h))
x = ag.fill_maze(outline, spacing=20,
                 style=ag.Maze_Style_Round(rel_thickness=0.3),
                 rotation=45)
ag.set_style(x['members'], 'fill', 'blue')

c.new(x)
c.png("png/mazes4.png")