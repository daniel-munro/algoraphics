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
size = ag.Exponential(2.2, stdev=1).values(len(points))
x1 = [ag.circle(c=p, r=size[i], fill=color) for i, p in enumerate(points)]
ag.reposition(x1, (w / 2, h - 50), "center", "top")
c.new(ag.shuffled(x1))

points = ex.text_points("HIJKLM", 50, pt_spacing=0.5, char_spacing=0.15)
ag.jitter_points(points, 2)
size = ag.Exponential(2.2, stdev=1).values(len(points))
x2 = [ag.circle(c=p, r=size[i], fill=color) for i, p in enumerate(points)]
ag.reposition(x2, (w / 2, h - 150), "center", "top")
c.add(ag.shuffled(x2))

points = ex.text_points("0123456789", 50, pt_spacing=0.5, char_spacing=0.15)
ag.jitter_points(points, 2)
size = ag.Exponential(2.2, stdev=1).values(len(points))
x3 = [ag.circle(c=p, r=size[i], fill=color) for i, p in enumerate(points)]
ag.reposition(x3, (w / 2, h - 250), "center", "top")
c.add(ag.shuffled(x3))

c.png("png/text1.png")


####################
# Double dots text #
####################

points = ex.text_points("NOPQRST", 40, pt_spacing=0.3, char_spacing=0.15)
ag.jitter_points(points, 8)
size = ag.Exponential(2.2, stdev=1).values(len(points))
x1a = [ag.circle(c=p, r=size[i], fill="black") for i, p in enumerate(points)]

points = ex.text_points("NOPQRST", 40, pt_spacing=1, char_spacing=0.15)
ag.jitter_points(points, 2)
size = ag.Exponential(1.5, stdev=0.5).values(len(points))
x1b = [ag.circle(c=p, r=size[i], fill="white") for i, p in enumerate(points)]

ag.reposition([x1a, x1b], (w / 2, h - 50), "center", "top")
c.new(x1a, x1b)

points = ex.text_points("UVWXYZ", 40, pt_spacing=0.3, char_spacing=0.15)
ag.jitter_points(points, 8)
size = ag.Exponential(2.2, stdev=1).values(len(points))
x2a = [ag.circle(c=p, r=size[i], fill="black") for i, p in enumerate(points)]

points = ex.text_points("UVWXYZ", 40, pt_spacing=1, char_spacing=0.15)
ag.jitter_points(points, 2)
size = ag.Exponential(1.5, stdev=0.5).values(len(points))
x2b = [ag.circle(c=p, r=size[i], fill="white") for i, p in enumerate(points)]

ag.reposition([x2a, x2b], (w / 2, h - 150), "center", "top")
c.add(x2a, x2b)

points = ex.text_points(".,!?:;'\"/", 40, pt_spacing=0.3, char_spacing=0.15)
ag.jitter_points(points, 8)
size = ag.Exponential(2.2, stdev=1).values(len(points))
x3a = [ag.circle(c=p, r=size[i], fill="black") for i, p in enumerate(points)]

points = ex.text_points(".,!?:;'\"/", 40, pt_spacing=1, char_spacing=0.15)
ag.jitter_points(points, 2)
size = ag.Exponential(1.5, stdev=0.5).values(len(points))
x3b = [ag.circle(c=p, r=size[i], fill="white") for i, p in enumerate(points)]

ag.reposition([x3a, x3b], (w / 2, h - 250), "center", "top")
c.add(x3a, x3b)

c.png("png/text2.png")


#############
# Hazy text #
#############

pts = ex.text_points("abcdefg", height=50, pt_spacing=1/4, char_spacing=0.15)
dists = ag.Uniform(0, 10).values(len(pts))
points = [ag.endpoint(p, ag.Uniform(0, 360).value(), dists[i]) for i, p in enumerate(pts)]
radii = 0.5 * np.sqrt(10 - np.array(dists))
x1 = [ag.circle(c=p, r=radii[i]) for i, p in enumerate(points)]
ag.reposition(x1, (w / 2, h - 100), "center", "top")
ag.set_style(x1, "fill", "green")

pts = ex.text_points("hijklm", height=50, pt_spacing=1/4, char_spacing=0.15)
dists = ag.Uniform(0, 10).values(len(pts))
points = [ag.endpoint(p, ag.Uniform(0, 360).value(), dists[i]) for i, p in enumerate(pts)]
radii = 0.5 * np.sqrt(10 - np.array(dists))
x2 = [ag.circle(c=p, r=radii[i]) for i, p in enumerate(points)]
ag.reposition(x2, (w / 2, h - 250), "center", "top")
ag.set_style(x2, "fill", "green")

c.new(x1, x2)
c.png("png/text3.png")


#################
# Squiggle text #
#################

strokes = ex.text_points("nopqrst", 60, pt_spacing=1,
                         char_spacing=0.2, grouping='strokes')
for stroke in strokes:
    ag.jitter_points(stroke, 10)
x1 = [ag.spline(points=stroke) for stroke in strokes]
ag.reposition(x1, (w / 2, h - 100), "center", "top")

strokes = ex.text_points("uvwxyz", 60, pt_spacing=1,
                         char_spacing=0.2, grouping='strokes')
for stroke in strokes:
    ag.jitter_points(stroke, 10)
x2 = [ag.spline(points=stroke) for stroke in strokes]
ag.reposition(x2, (w / 2, h - 250), "center", "top")

c.new(x1, x2)
c.png("png/text4.png")
