import os
import algoraphics as ag

os.chdir(os.path.dirname(os.path.abspath(__file__)))

c = ag.Canvas(400, 400)

#################
# Filament fill #
#################


def filament_fill(bounds):
    c = ((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2)
    r = ag.distance(c, (bounds[2], bounds[3]))
    start = ag.rand_point_on_circle(c, r)
    dir_start = ag.direction_to(start, c)
    filament = ag.filament(
        start=start,
        direction=ag.Delta(dir_start, delta=ag.Uniform(min=-20, max=20)),
        width=ag.Uniform(min=8, max=12),
        seg_length=ag.Uniform(min=8, max=12),
        n_segments=int(2.2 * r / 10),
    )
    color = ag.Color(hsl=(ag.Uniform(min=0, max=0.15), 1, 0.5))
    ag.set_style(filament, "fill", color)
    return filament


outline = ag.circle(c=(200, 200), r=100)
x = ag.fill_region(outline, filament_fill)
ag.add_shadows(x["members"])

c.add(x)
c.png("png/fill1.png")


######################################
# Wrapping paper-style object tiling #
######################################


def doodle1_fun():
    d = ag.circle(c=(0.5, 0.5), r=0.45)
    ag.set_style(d, "fill", "green")
    return d


def doodle2_fun():
    d = [
        ag.circle(c=(0.5, 0.5), r=0.45),
        ag.circle(c=(1, 0.5), r=0.45),
        ag.circle(c=(1.5, 0.5), r=0.45),
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


doodle1 = ag.Doodle(doodle1_fun, footprint=[[True]])
doodle2 = ag.Doodle(doodle2_fun, footprint=[[True, True]])
doodle3 = ag.Doodle(doodle3_fun, footprint=[[True, True, True], [False, True, False]])
doodles = [doodle1, doodle2, doodle3]

outline = ag.circle(c=(200, 200), r=180)

x = ag.fill_wrapping_paper(outline, 30, doodles, rotate=True)

c.new(x)
c.png("png/fill2.png")


#############
# Spot fill #
#############

outline = ag.circle(c=(200, 200), r=150)
color = ag.Color(
    hue=ag.Uniform(min=0.6, max=0.8), sat=0.7, li=ag.Uniform(min=0.5, max=0.7)
)
x = ag.fill_spots(outline)
ag.set_style(x, "fill", color)

c.new(x)
c.png("png/fill3.png")
