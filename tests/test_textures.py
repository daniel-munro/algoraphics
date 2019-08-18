import os
import algoraphics as ag

os.chdir(os.path.dirname(os.path.abspath(__file__)))

c = ag.Canvas(400, 400)

###########
# Shadows #
###########

x = [
    ag.Circle(c=(100, 150), r=50, stroke="#FFDDDD"),
    ag.Circle(c=(150, 100), r=50, stroke="#DDDDFF"),
]
ag.set_style(x, "stroke-width", 20)
ag.add_shadows(x, stdev=20, darkness=0.5)

y = [[
    ag.Circle(c=(300, 250), r=50, fill="#FFDDDD"),
    ag.Circle(c=(250, 300), r=50, fill="#DDDDFF"),
]]
# ag.add_paper_texture(y)

# Note that add_shadows adds shadows to the immediate list elements as
# wholes, meaning the top circle should not project a shadow onto the
# one behind it.
ag.add_shadows(y, stdev=20, darkness=0.5)

c.add(x, y)
c.png("png/textures1.png")
