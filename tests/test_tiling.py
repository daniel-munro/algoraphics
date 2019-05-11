import os
import algoraphics as ag

os.chdir(os.path.dirname(os.path.abspath(__file__)))

c = ag.Canvas(400, 400)

#################
# Polygon tiles #
#################

outline = ag.circle(c=(200, 200), r=150)
colors = ag.Color(hue=ag.Uniform(min=0, max=0.15), sat=0.8, li=0.5)
x = ag.tile_region(outline, shape="polygon", tile_size=500)
ag.set_style(x["members"], "fill", colors)

c.add(x)
c.png("png/tiling1.png")


##################
# Triangle tiles #
##################

outline = ag.circle(c=(200, 200), r=150)
colors = ag.Color(hue=ag.Uniform(min=0, max=0.15), sat=0.8, li=0.5)
x = ag.tile_region(outline, shape="triangle", tile_size=500)
ag.set_style(x["members"], "fill", colors)

c.new(x)
c.png("png/tiling2.png")


#################
# Polygon edges #
#################

outline = ag.circle(c=(200, 200), r=150)
colors = ag.Color(
    hue=ag.Uniform(min=0.6, max=0.8), sat=0.7, li=ag.Uniform(min=0.5, max=0.7)
)
x = ag.tile_region(outline, shape="polygon", edges=True, tile_size=1000)
ag.set_style(x["members"], "stroke", colors)
ag.set_style(x["members"], "stroke-width", 2)

c.new(x)
c.png("png/tiling3.png")


##################
# Triangle edges #
##################

outline = ag.circle(c=(200, 200), r=150)
color = ag.Color(
    hue=ag.Uniform(min=0.6, max=0.8), sat=0.7, li=ag.Uniform(min=0.5, max=0.7)
)
x = ag.tile_region(outline, shape="triangle", edges=True, tile_size=1000)
ag.set_style(x["members"], "stroke", color)
ag.set_style(x["members"], "stroke-width", 2)

c.new(x)
c.png("png/tiling4.png")


####################
# Nested triangles #
####################

outline = ag.circle(c=(200, 200), r=150)
color = ag.Color(hue=ag.Uniform(min=0, max=0.15), sat=0.8, li=0.5)
x = ag.fill_nested_triangles(outline, min_level=2, max_level=5, color=color)

c.new(x)
c.png("png/tiling5.png")
