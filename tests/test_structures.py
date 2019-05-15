import os
import algoraphics as ag

os.chdir(os.path.dirname(os.path.abspath(__file__)))

c = ag.Canvas(400, 400)

#########################
# Fixed-width filaments #
#########################

dirs = [ag.Delta(d, delta=ag.Uniform(min=-20, max=20)) for d in range(360)[::10]]
width = ag.Uniform(min=8, max=12)
length = ag.Uniform(min=8, max=12)
# x = [ag.filament(start=(w / 2., h / 2.), direction=d, width=width,
#                  seg_length=length, n_segments=40) for d in dirs]
x = [
    ag.filament(
        start=(c.width / 2, c.height / 2),
        direction=d,
        width=width,
        seg_length=length,
        n_segments=20,
    )
    for d in dirs
]

# ag.set_style(x, 'fill', ag.Color(hsl=(ag.Uniform(min=0.6, max=0.75), 1, 0.5)))
ag.set_style(x, "fill", ag.Color(hsl=(ag.Uniform(min=0, max=0.15), 1, 0.5)))

c.add(x)
c.png("png/structures1.png")


###########################################
# Fixed-width filaments with smooth curls #
###########################################

direc = ag.Delta(
    90, delta=ag.Delta(0, min=-20, max=20, delta=ag.Uniform(min=-3, max=3))
)
x = [
    ag.filament(start=(z, -10), direction=direc, width=8, seg_length=10, n_segments=50)
    for z in range(c.width)[::30]
]

ag.set_style(x, "fill", ag.Color(hsl=(0.33, 1, ag.Uniform(min=0.15, max=0.35))))

c.new(x)
c.png("png/structures2.png")


#################################
# Tapered filaments (tentacles) #
#################################

dirs = [
    ag.Delta(d, delta=ag.Delta(0, min=-20, max=20, delta=ag.Uniform(min=-30, max=30)))
    for d in range(360)[::15]
]
# n_seg = 50
# n_seg = 30
# width = ag.Param(10, delta=-10/n_seg)
# length = ag.Param(10, delta=-5/n_seg)
# x = [ag.filament(start=(w / 2., h / 2.), direction=d, width=width,
#                  seg_length=length, n_segments=n_seg) for d in dirs]
x = [
    ag.tentacle(
        start=(c.width / 2, c.height / 2),
        length=225,
        direction=d,
        width=15,
        seg_length=10,
    )
    for d in dirs
]
# n_seg = 40
# width = ag.Param(10, delta=-10 / n_seg)
# length = ag.Param(10, delta=-5 / n_seg)
# y = [ag.filament(start=(w / 2., h / 2.), direction=d, width=width,
#                  seg_length=length, n_segments=n_seg) for d in dirs]
ag.set_style(x, "fill", ag.Color(hsl=(ag.Uniform(min=0.6, max=0.75), 1, 0.5)))
# ag.set_style(y, 'fill', ag.Color(hsl=(ag.Uniform(min=0, max=0.15), 1, 0.5)))

c.new(x)
c.png("png/structures3.png")


###################################################
# Tapered filaments (tentacles) with smooth curls #
###################################################

# direc = ag.Param(90, delta=ag.Param(0, min=-20, max=20,
#                                     delta=ag.Uniform(min=-5, max=5)))
# # n_seg = 80
# n_seg = 50
# width = ag.Param(20, delta=-20 / n_seg)
# length = ag.Param(16, delta=-8 / n_seg)
# x = [ag.filament(start=(z, -10), direction=direc, width=width,
#                  seg_length=length, n_segments=n_seg) for z in range(w)[::30]]
# # n_seg = 60
# # width = ag.Param(20, delta=-20 / n_seg)
# # length = ag.Param(16, delta=-8 / n_seg)
# # y = [ag.filament(start=(z, -10), direction=direc, width=width,
# #                  seg_length=length, n_segments=n_seg) for z in range(w)[::50]]

# ag.set_style(x, 'fill',
#              ag.Color(hsl=(0.33, 1, ag.Uniform(min=0.15, max=0.35))))
# # ag.set_style(y, 'fill', ag.Color(hsl=(0.33, 1, ag.Uniform(min=0.35, max=0.55))))

# ag.write_SVG(x, w, h, 'svg/filaments4.svg')
# ag.to_PNG('svg/filaments4.svg', 'png/filaments4.png')


################################################
# Blow-paint effects (polygon, line, and spot) #
################################################

pts1 = [(50, 50), (50, 100), (100, 70), (150, 130), (200, 60)]
x1 = ag.blow_paint_area(pts1)

pts2 = [(250, 50), (350, 50), (300, 200)]
x2 = ag.blow_paint_area(pts2, spacing=20, length=20, len_dev=0.4, width=8)
ag.set_style(x2, "fill", "orange")

pts3 = [(50, 300), (100, 350), (200, 250), (300, 300)]
y = ag.blow_paint_line(pts3, line_width=8, spacing=15, length=30, len_dev=0.4, width=6)
ag.set_style(y, "fill", "red")

z = ag.blow_paint_spot((350, 350), length=20)
ag.set_style(z, "stroke", "blue")

c.new(x1, x2, y, z)
c.png("png/structures4.png")


################################
# Trees branching from a point #
################################

x = [
    ag.tree(
        (200, 200),
        direction=d,
        branch_length=ag.Uniform(min=8, max=20),
        theta=ag.Uniform(min=15, max=20),
        p=ag.Delta(1, delta=-0.08),
    )
    for d in range(360)[::20]
]
ag.set_style(
    x,
    "stroke",
    ag.Color(hue=ag.Normal(0.12, stdev=0.05), sat=ag.Uniform(0.4, 0.7), li=0.3),
)

c.new(x)
c.png("png/structures5.png")
