import os
import numpy as np
import algoraphics as ag
import algoraphics.extras as ex

os.chdir(os.path.dirname(os.path.abspath(__file__)))

w, h = 400, 400
c = ag.Canvas(w, h)

#################
# Splatter text #
#################

color = ag.Color(hue=ag.Uniform(0, 0.15), sat=0.8, li=0.5)

points = ex.text_points("ABCDEFG", 50, pt_spacing=0.5, char_spacing=0.15)
ag.jitter_points(points, 2)
points = [ag.Translation(p, (20, 300)) for p in points]
x1 = [ag.Circle(c=p, r=ag.Exponential(2.2, stdev=1)) for p in points]
ag.set_styles(x1, "fill", color)
c.new(ag.shuffled(x1))

points = ex.text_points("HIJKLM", 50, pt_spacing=0.5, char_spacing=0.15)
ag.jitter_points(points, 2)
points = [ag.Translation(p, (20, 200)) for p in points]
x2 = [ag.Circle(c=p, r=ag.Exponential(2.2, stdev=1)) for p in points]
ag.set_styles(x2, "fill", color)
c.add(ag.shuffled(x2))

points = ex.text_points("0123456789", 50, pt_spacing=0.5, char_spacing=0.15)
ag.jitter_points(points, 2)
points = [ag.Translation(p, (20, 100)) for p in points]
x3 = [ag.Circle(c=p, r=ag.Exponential(2.2, stdev=1)) for p in points]
ag.set_styles(x3, "fill", color)
c.add(ag.shuffled(x3))

c.png("png/text1.png")


####################
# Double dots text #
####################

points = ex.text_points("NOPQRST", 40, pt_spacing=0.3, char_spacing=0.15)
ag.jitter_points(points, 8)
points = [ag.Translation(p, (20, 300)) for p in points]
x1a = [ag.Circle(c=p, r=ag.Exponential(2.2, stdev=1), fill="black") for p in points]

points = ex.text_points("NOPQRST", 40, pt_spacing=1, char_spacing=0.15)
ag.jitter_points(points, 2)
points = [ag.Translation(p, (20, 300)) for p in points]
x1b = [ag.Circle(c=p, r=ag.Exponential(1.5, stdev=0.5), fill="white") for p in points]

# ag.reposition([x1a, x1b], (w / 2, h - 50), "center", "top")
c.new(x1a, x1b)

points = ex.text_points("UVWXYZ", 40, pt_spacing=0.3, char_spacing=0.15)
ag.jitter_points(points, 8)
points = [ag.Translation(p, (20, 200)) for p in points]
x2a = [
    ag.Circle(c=p, r=ag.Exponential(2.2, stdev=1), fill="black")
    for i, p in enumerate(points)
]

points = ex.text_points("UVWXYZ", 40, pt_spacing=1, char_spacing=0.15)
ag.jitter_points(points, 2)
points = [ag.Translation(p, (20, 200)) for p in points]
x2b = [
    ag.Circle(c=p, r=ag.Exponential(1.5, stdev=0.5), fill="white")
    for i, p in enumerate(points)
]

# ag.reposition([x2a, x2b], (w / 2, h - 150), "center", "top")
c.add(x2a, x2b)

points = ex.text_points(".,!?:;'\"/", 40, pt_spacing=0.3, char_spacing=0.15)
ag.jitter_points(points, 8)
points = [ag.Translation(p, (20, 100)) for p in points]
x3a = [
    ag.Circle(c=p, r=ag.Exponential(2.2, stdev=1), fill="black")
    for i, p in enumerate(points)
]

points = ex.text_points(".,!?:;'\"/", 40, pt_spacing=1, char_spacing=0.15)
ag.jitter_points(points, 2)
points = [ag.Translation(p, (20, 100)) for p in points]
x3b = [
    ag.Circle(c=p, r=ag.Exponential(1.5, stdev=0.5), fill="white")
    for i, p in enumerate(points)
]

# ag.reposition([x3a, x3b], (w / 2, h - 250), "center", "top")
c.add(x3a, x3b)

c.png("png/text2.png")


#############
# Hazy text #
#############

pts = ex.text_points("abcdefg", height=50, pt_spacing=1 / 4, char_spacing=0.15)
points = [ag.Translation(p, (20, 250)) for p in pts]
points = [
    ag.Move(p, direction=ag.Uniform(0, 360), distance=ag.Uniform(0, 10)) for p in points
]
x1 = []
for p in points:
    radius = 0.5 * np.sqrt(10 - p.distance.state())
    x1.append(ag.Circle(c=p, r=radius))
# ag.reposition(x1, (w / 2, h - 100), "center", "top")
ag.set_style(x1, "fill", "green")

pts = ex.text_points("hijklm", height=50, pt_spacing=1 / 4, char_spacing=0.15)
points = [ag.Translation(p, (20, 100)) for p in pts]
points = [
    ag.Move(p, direction=ag.Uniform(0, 360), distance=ag.Uniform(0, 10)) for p in points
]
x2 = []
for p in points:
    radius = 0.5 * np.sqrt(10 - p.distance.state())
    x2.append(ag.Circle(c=p, r=radius))
# ag.reposition(x2, (w / 2, h - 250), "center", "top")
ag.set_style(x2, "fill", "green")

c.new(x1, x2)
c.png("png/text3.png")


#################
# Squiggle text #
#################

strokes = ex.text_points(
    "nopqrst", 60, pt_spacing=1, char_spacing=0.2, grouping="strokes"
)
for stroke in strokes:
    ag.jitter_points(stroke, 10)
    for i, p in enumerate(stroke):
        stroke[i] = ag.Translation(p, (20, 250))
x1 = [ag.Spline(points=stroke) for stroke in strokes]
# ag.reposition(x1, (w / 2, h - 100), "center", "top")

strokes = ex.text_points(
    "uvwxyz", 60, pt_spacing=1, char_spacing=0.2, grouping="strokes"
)
for stroke in strokes:
    ag.jitter_points(stroke, 10)
    for i, p in enumerate(stroke):
        stroke[i] = ag.Translation(p, (20, 100))
x2 = [ag.Spline(points=stroke) for stroke in strokes]
# ag.reposition(x2, (w / 2, h - 250), "center", "top")

c.new(x1, x2)
c.png("png/text4.png")
