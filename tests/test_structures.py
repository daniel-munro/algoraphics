import os
import algoraphics as ag
import algoraphics.extras as ex

os.chdir(os.path.dirname(os.path.abspath(__file__)))

c = ag.Canvas(400, 400)

#########################
# Fixed-width filaments #
#########################

start = (c.width / 2, c.height / 2)
x = []
for direc in range(360)[::10]:
    backbone = [start]
    for i in range(20):
        backbone.append(
            ag.Move(backbone[-1], direction=direc, distance=ag.Uniform(min=9, max=12))
        )
        direc = direc + ag.Uniform(min=-20, max=20)
    x.append(ex.filament(backbone, width=ag.Uniform(min=8, max=12)))
ag.set_styles(x, "fill", ag.Color(ag.Uniform(min=0, max=0.15), 1, 0.5))

c.add(x)
c.png("png/structures1.png")


###########################################
# Fixed-width filaments with smooth curls #
###########################################

x = []
for z in range(c.width)[::30]:
    deldirec = 0
    direc = 90
    backbone = [(z, -10)]
    for i in range(50):
        backbone.append(
            ag.Move(backbone[-1], direction=direc, distance=10)
        )
        deldirec = ag.Clip(deldirec + ag.Uniform(min=-3, max=3), min=-20, max=20)
        direc = direc + deldirec
    x.append(ex.filament(backbone, width=8))
ag.set_styles(x, "fill", ag.Color(0.33, 1, ag.Uniform(min=0.15, max=0.35)))

c.new(x)
c.png("png/structures2.png")


#############
# Tentacles #
#############

start = (c.width / 2, c.height / 2)
x = []
for d in range(360)[::15]:
    deldirec = 0
    direc = d
    distance = 10
    backbone = [start]
    for i in range(25):
        backbone.append(
            ag.Move(backbone[-1], direction=direc, distance=distance)
        )
        deldirec = ag.Clip(deldirec + ag.Uniform(min=-30, max=30), min=-20, max=20)
        direc = direc + deldirec
        distance -= 0.2
    x.append(ex.tentacle(backbone, width=15))
ag.set_styles(x, "fill", ag.Color(ag.Uniform(min=0.6, max=0.75), 1, 0.5))

c.new(x)
c.png("png/structures3.png")


################################################
# Blow-paint effects (polygon, line, and spot) #
################################################

pts1 = [(50, 50), (50, 100), (100, 70), (150, 130), (200, 60)]
x1 = ex.blow_paint_area(pts1)

pts2 = [(250, 50), (350, 50), (300, 200)]
x2 = ex.blow_paint_area(pts2, spacing=20, length=20, len_dev=0.4, width=8)
ag.set_style(x2, "fill", "orange")

pts3 = [(50, 300), (100, 350), (200, 250), (300, 300)]
y = ex.blow_paint_line(pts3, line_width=8, spacing=15, length=30, len_dev=0.4, width=6)
ag.set_style(y, "fill", "red")

z = ex.blow_paint_spot((350, 350), length=20)
ag.set_style(z, "stroke", "blue")

c.new(x1, x2, y, z)
c.png("png/structures4.png")


################################
# Trees branching from a point #
################################

x = [
    ex.tree(
        (200, 200),
        direction=d,
        branch_length=ag.Uniform(min=8, max=20),
        theta=ag.Uniform(min=15, max=20),
        p=1,
        delta_p=-0.08,
    )
    for d in range(360)[::20]
]
ag.set_styles(
    x,
    "stroke",
    ag.Color(hue=ag.Normal(0.12, stdev=0.05), sat=ag.Uniform(0.4, 0.7), li=0.3),
)

c.new(x)
c.png("png/structures5.png")
