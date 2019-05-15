import os
import algoraphics as ag

os.chdir(os.path.dirname(os.path.abspath(__file__)))

w, h = 400, 200
c = ag.Canvas(w, h)

#############
# Circles 1 #
#############

center = (ag.Uniform(10, w - 10), ag.Uniform(10, h - 10))
radius = ag.Uniform(1, 10)
color = ag.Color(hue=ag.Uniform(0.4, 0.6), sat=0.9, li=0.5)
x = [ag.circle(center, radius) for i in range(100)]
ag.set_style(x, "fill", color)

c.add(x)
c.png("png/param1.png")


#############
# Circles 2 #
#############

center = (ag.Param([100, 300]), 100)
radius = ag.Delta(100, delta=-1)
color = ag.Color(hue=0.8, sat=0.9, li=ag.Uniform(0, 1))
x = [ag.circle(center, radius) for i in range(100)]
ag.set_style(x, "fill", color)

c.new(x)
c.png("png/param2.png")


#############
# Circles 3 #
#############

center = (ag.Delta(0, delta=4), ag.Uniform(0, h))
radius = ag.Uniform(5, 30)
color = ag.Color(hue=ag.Delta(0, delta=0.005), sat=0.9, li=0.5)
x = [ag.circle(center, radius) for i in range(100)]
ag.set_style(x, "fill", color)

c.new(x)
c.png("png/param3.png")


#################
# Nested deltas #
#################

x = []

p2y = ag.Delta(start=170, delta=-0.25)
x.append([ag.line((i * 4, 170), (i * 4, p2y)) for i in range(100)])

p2y = ag.Delta(start=100, min=70, max=130, delta=ag.Uniform(-5, 5))
x.append([ag.line((i * 4, 100), (i * 4, p2y)) for i in range(100)])

p2y = ag.Delta(
    start=30,
    min=0,
    max=60,
    delta=ag.Delta(start=0, min=-2, max=2, delta=ag.Uniform(-2, 2)),
)
x.append([ag.line((i * 4, 30), (i * 4, p2y)) for i in range(100)])
ag.set_style(x, "stroke-width", 2)

c.new(x)
c.png("png/param4.png")


##############
# List param #
##############

center = (ag.Uniform(10, w - 10), ag.Uniform(10, h - 10))
radius = ag.Uniform(5, 15)
color = ag.Param(["blue", "blue", "blue", "red"])
x = [ag.circle(center, radius) for i in range(100)]
ag.set_style(x, "fill", color)

c.new(x)
c.png("png/param5.png")


############
# Cyclical #
############

wave = ag.Cyclical(
    low=ag.Delta(min=0, max=50, delta=ag.Uniform(-5, 5)),
    high=ag.Delta(min=150, max=200, delta=ag.Uniform(-5, 5)),
    period=ag.Delta(min=10, max=30, delta=ag.Uniform(-2, 2)),
)
pts = [(i, wave.value()) for i in range(400)]
x = ag.spline(pts)

c.new(x)
c.png("png/param6.png")


#########
# Place #
#########

place = ag.Place(
    ref=(200, 0),
    direction=ag.Normal(90, 30),
    distance=ag.Exponential(mean=50, stdev=100, sigma=3),
)
x = [ag.circle(p, 2, fill="purple") for p in place.values(10000)]

c.new(x)
c.png("png/param7.png")


##########
# Wander #
##########

path = ag.Wander(
    start=(0, 100),
    direction=ag.Delta(0, ag.Delta(0, min=-20, max=20, delta=ag.Uniform(-3, 3))),
    distance=ag.Uniform(8, 12),
)
radius = ag.Uniform(2, 4)
x = [ag.circle(path.value(), radius) for i in range(300)]

c.new(x)
c.png("png/param8.png")
