import os
import algoraphics as ag

os.chdir(os.path.dirname(os.path.abspath(__file__)))

w, h = 400, 200
c = ag.Canvas(w, h)

#############
# Circles 1 #
#############

# center = (ag.Uniform(10, w - 10), ag.Uniform(10, h - 10))
# radius = ag.Uniform(1, 10)
# color = ag.Color(hue=ag.Uniform(0.4, 0.6), sat=0.9, li=0.5)
# x = [ag.Circle(center, radius) for i in range(100)]
x = 100 * ag.Circle(
    c=(ag.Uniform(10, w - 10), ag.Uniform(10, h - 10)),
    r=ag.Uniform(1, 10),
    fill=ag.Color(hue=ag.Uniform(0.4, 0.6), sat=0.9, li=0.5),
)

c.add(x)
c.png("png/param1.png")


#############
# Circles 2 #
#############

x = [
    ag.Circle(
        c=(ag.Param([100, 300]), 100),
        r=r,
        fill=ag.Color(hue=0.8, sat=0.9, li=ag.Uniform(0, 1)),
    )
    for r in range(100, 0, -1)
]

c.new(x)
c.png("png/param2.png")


#############
# Circles 3 #
#############

# center = (ag.Delta(0, delta=4), ag.Uniform(0, h))
# color = ag.Color(hue=ag.Delta(0, delta=0.005), sat=0.9, li=0.5)
# x = [ag.Circle(c=(4 * i, ag.Uniform(0, h)), r=ag.Uniform(5, 30)) for i in range(100)]
x = 100 * ag.Circle(c=(ag.Uniform(0, 400), ag.Uniform(0, h)), r=ag.Uniform(5, 30))
for circle in x:
    color = ag.Color(hue=circle.c.state(0)[0] / 500, sat=0.9, li=0.5)
    ag.set_style(circle, "fill", color)

c.new(x)
c.png("png/param3.png")


#################
# Nested deltas #
#################

x = []

p2y = 170
for i in range(100):
    x.append(ag.Line((i * 4, 170), (i * 4, p2y)))
    p2y = p2y - 0.25

p2y = 100
for i in range(100):
    x.append(ag.Line((i * 4, 100), (i * 4, p2y)))
    p2y = ag.Clip(p2y + ag.Uniform(-5, 5), min=70, max=130)

p2y = 30
delta = 0
for i in range(100):
    x.append(ag.Line((i * 4, 30), (i * 4, p2y)))
    delta = ag.Clip(delta + ag.Uniform(-2, 2), min=-2, max=2)
    p2y = ag.Clip(p2y + delta, min=0, max=60)

ag.set_style(x, "stroke-width", 2)
c.new(x)
c.png("png/param4.png")

# Redundant with param2:
# ##############
# # List param #
# ##############

# x = [
#     ag.Circle(
#         c=(ag.Uniform(10, w - 10), ag.Uniform(10, h - 10)),
#         r=ag.Uniform(5, 15),
#         fill=ag.Param(["blue", "blue", "blue", "red"]),
#     )
#     for i in range(100)
# ]

# c.new(x)
# c.png("png/param5.png")

# Needs rewrite:
# ############
# # Cyclical #
# ############

# wave = ag.Cyclical(
#     low=ag.Delta(min=0, max=50, delta=ag.Uniform(-5, 5)),
#     high=ag.Delta(min=150, max=200, delta=ag.Uniform(-5, 5)),
#     period=ag.Delta(min=10, max=30, delta=ag.Uniform(-2, 2)),
# )
# pts = [(i, wave.value()) for i in range(400)]
# x = ag.Spline(pts)

# c.new(x)
# c.png("png/param6.png")


#########
# Place #
#########

x = [
    ag.Circle(
        c=ag.Move(
            ref=(200, 0),
            direction=ag.Normal(90, 30),
            distance=ag.Exponential(mean=50, stdev=100, sigma=3),
        ),
        r=2,
        fill="purple",
    )
    for i in range(10000)
]

c.new(x)
c.png("png/param7.png")


##########
# Wander #
##########

# path = ag.Wander(
#     start=(0, 100),
#     direction=ag.Delta(0, ag.Delta(0, min=-20, max=20, delta=ag.Uniform(-3, 3))),
#     distance=ag.Uniform(8, 12),
# )
# radius = ag.Uniform(2, 4)
# x = [ag.Circle(path.value(), radius) for i in range(300)]

x = []
center = (0, 200)
direc = 0
deltadirec = 0
for i in range(300):
    x.append(ag.Circle(center, r=ag.Uniform(2, 4)))
    deltadirec = ag.Clip(deltadirec + ag.Uniform(-5, 5), -10, 10)
    direc = direc + deltadirec
    center = ag.Move(center, direction=direc, distance=ag.Uniform(8, 12))
c = ag.Canvas(400, 400)
c.add(x)
c.png("png/param8.png")


#########################
# Wander with animation #
#########################

x = []
center = (0, 200)
direc = 0
deltadirec = 0
for i in range(100):
    deltar = ag.Dynamic(0, ag.Uniform(-0.2, 0.2, static=False), min=-0.2, max=0.2)
    r = ag.Dynamic(ag.Uniform(2, 4), delta=deltar, min=2, max=4)
    x.append(ag.Circle(center, r))
    # deltadirec = ag.Clip(deltadirec + ag.Uniform(-5, 5), -10, 10)
    deldeldir = ag.Dynamic(
        ag.Uniform(-5, 5), delta=ag.Uniform(-0.2, 0.2, static=False), min=-5, max=5
    )
    deltadirec = ag.Clip(deltadirec + deldeldir, -10, 10)
    direc = direc + deltadirec
    deltadist = ag.Dynamic(
        ag.Uniform(-2, 2), delta=ag.Uniform(-0.5, 0.5, static=False), min=-2, max=2
    )
    dist = ag.Dynamic(ag.Uniform(8, 12), delta=deltadist, min=8, max=12)
    center = ag.Move(center, direction=direc, distance=dist)
c = ag.Canvas(400, 400)
c.add(x)
# c.png("png/param9.png")
c.gif("png/param9.gif", fps=12, seconds=4)
