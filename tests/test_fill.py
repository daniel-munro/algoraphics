import os
import numpy as np
import algoraphics as ag
import algoraphics.extras as ex

os.chdir(os.path.dirname(os.path.abspath(__file__)))

c = ag.Canvas(400, 400)

#################
# Filament fill #
#################


def rand_point_on_circle(c, r):
    theta = np.random.uniform(-np.pi, np.pi)
    return (c[0] + np.cos(theta) * r, c[1] + np.sin(theta) * r)


def filament_fill(bounds):
    c = ((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2)
    r = ag.distance(c, (bounds[2], bounds[3]))
    start = rand_point_on_circle(c, r)
    direc = ag.direction_to(start, c)
    backbone = [start]
    for i in range(int(2.2 * r / 10)):
        backbone.append(
            ag.Move(backbone[-1], direction=direc, distance=ag.Uniform(min=8, max=12))
        )
        direc = direc + ag.Uniform(min=-20, max=20)
    filament = ex.filament(backbone, width=ag.Uniform(min=8, max=12))
    color = ag.Color(ag.Uniform(min=0, max=0.15), 1, 0.5)
    ag.set_styles(filament, "fill", color)
    return filament


outline = ag.Circle(c=(200, 200), r=100)
x = ex.fill_region(outline, filament_fill, min_coverage=0.99)
ag.add_shadows(x.members)

c.add(x)
c.png("png/fill1.png")


######################################
# Wrapping paper-style object tiling #
######################################


def doodle1_fun():
    d = ag.Circle(c=(0.5, 0.5), r=0.45)
    ag.set_style(d, "fill", "green")
    return d


def doodle2_fun():
    d = [
        ag.Circle(c=(0.5, 0.5), r=0.45),
        ag.Circle(c=(1, 0.5), r=0.45),
        ag.Circle(c=(1.5, 0.5), r=0.45),
    ]
    ag.set_style(d, "fill", "red")
    return d


def doodle3_fun():
    d = [
        ag.rectangle(start=(0.2, 1.2), w=2.6, h=0.6),
        ag.rectangle(start=(1.2, 0.2), w=0.6, h=1.6),
    ]
    ag.set_style(d, "fill", "blue")
    return d


doodle1 = ex.Doodle(doodle1_fun, footprint=[[True]])
doodle2 = ex.Doodle(doodle2_fun, footprint=[[True, True]])
doodle3 = ex.Doodle(doodle3_fun, footprint=[[True, True, True], [False, True, False]])
doodles = [doodle1, doodle2, doodle3]

outline = ag.Circle(c=(200, 200), r=180)

x = ex.fill_wrapping_paper(outline, 30, doodles, rotate=True)

c.new(x)
c.png("png/fill2.png")


#############
# Spot fill #
#############

outline = ag.Circle(c=(200, 200), r=150)
color = ag.Color(
    hue=ag.Uniform(min=0.6, max=0.8), sat=0.7, li=ag.Uniform(min=0.5, max=0.7)
)
x = ex.fill_spots(outline)
ag.set_styles(x, "fill", color)

c.new(x)
c.png("png/fill3.png")
