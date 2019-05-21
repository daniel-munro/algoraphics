import os
import algoraphics as ag

os.chdir(os.path.dirname(os.path.abspath(__file__)))

c = ag.Canvas(400, 400)

#####################
# Shadows and paper #
#####################

x = [
    ag.circle(c=(100, 150), r=50, stroke="#FFDDDD"),
    ag.circle(c=(150, 100), r=50, stroke="#DDDDFF"),
]
ag.set_style(x, "stroke-width", 20)
ag.add_shadows(x, stdev=20, darkness=0.5)

y = [[
    ag.circle(c=(300, 250), r=50, fill="#FFDDDD"),
    ag.circle(c=(250, 300), r=50, fill="#DDDDFF"),
]]
ag.add_paper_texture(y)
# Note that add_shadows adds shadows to the immediate list elements as
# wholes, meaning the top circle should not project a shadow onto the
# one behind it.
ag.add_shadows(y, stdev=20, darkness=0.5)

c.add(x, y)
c.png("png/textures1.png")


#############
# Billowing #
#############

outline = ag.circle(c=(120, 120), r=100)
colors = [(0, 1, 0.3), (0.1, 1, 0.5), (0.2, 1, 0.5), (0.4, 1, 0.3)]
x = ag.billow_region(outline, colors, scale=200, gradient_mode="rgb")

outline = ag.circle(c=(280, 280), r=100)
colors = [(0, 1, 0.3), (0.6, 1, 0.3)]
y = ag.billow_region(outline, colors, scale=400, gradient_mode="hsv")

c.new(x, y)
c.png("png/textures2.png")
