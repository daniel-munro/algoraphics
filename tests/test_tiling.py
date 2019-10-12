import os
import algoraphics as ag
import algoraphics.extras as ex

os.chdir(os.path.dirname(os.path.abspath(__file__)))

c = ag.Canvas(400, 400)

#################
# Polygon tiles #
#################

outline = ag.Circle(c=(200, 200), r=150)
x = ex.tile_region(outline, shape="polygon", tile_size=500)
for tile in x.members:
    color = ag.Color(hue=ag.Uniform(min=0, max=0.15), sat=0.8, li=0.5)
    ag.set_style(tile, "fill", color)

c.add(x)
c.png("png/tiling1.png")


##################
# Triangle tiles #
##################

outline = ag.Circle(c=(200, 200), r=150)
x = ex.tile_region(outline, shape="triangle", tile_size=500)
for tile in x.members:
    color = ag.Color(hue=ag.Uniform(min=0, max=0.15), sat=0.8, li=0.5)
    ag.set_style(tile, "fill", color)

c.new(x)
c.png("png/tiling2.png")


#################
# Polygon edges #
#################

outline = ag.Circle(c=(200, 200), r=150)
x = ex.tile_region(outline, shape="polygon", edges=True, tile_size=1000)
for tile in x.members:
    color = ag.Color(
        hue=ag.Uniform(min=0.6, max=0.8), sat=0.7, li=ag.Uniform(min=0.5, max=0.7)
    )
    ag.set_style(tile, "stroke", color)
ag.set_style(x.members, "stroke-width", 2)

c.new(x)
c.png("png/tiling3.png")


##################
# Triangle edges #
##################

outline = ag.Circle(c=(200, 200), r=150)
x = ex.tile_region(outline, shape="triangle", edges=True, tile_size=1000)
for tile in x.members:
    color = ag.Color(
        hue=ag.Uniform(min=0.6, max=0.8), sat=0.7, li=ag.Uniform(min=0.5, max=0.7)
    )
    ag.set_style(tile, "stroke", color)
ag.set_style(x.members, "stroke-width", 2)

c.new(x)
c.png("png/tiling4.png")


####################
# Nested triangles #
####################

outline = ag.Circle(c=(200, 200), r=150)
color = ag.Color(hue=ag.Uniform(min=0, max=0.15), sat=0.8, li=0.5)
x = ex.fill_nested_triangles(
    outline, min_level=2, max_level=5, color=color, color2=(-0.5, 1, 0.5)
)

c.new(x)
c.png("png/tiling5.png")
