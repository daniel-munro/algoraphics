import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
import algoraphics as ag

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Polygon tiles
######################################################################

outline = ag.circle(c=(200, 200), r=150)
colors = ag.Color(hue=ag.Uniform(min=0, max=0.15), sat=0.8, li=0.5)
x = ag.tile_region(outline, shape='polygon', tile_size=500)
ag.set_style(x['members'], 'fill', colors)

ag.write_SVG(x, w, h, 'svg/tiling1.svg')
ag.to_PNG('svg/tiling1.svg', 'png/tiling1.png')


######################################################################
# Triangle tiles
######################################################################

outline = ag.circle(c=(200, 200), r=150)
colors = ag.Color(hue=ag.Uniform(min=0, max=0.15), sat=0.8, li=0.5)
x = ag.tile_region(outline, shape='triangle', tile_size=500)
ag.set_style(x['members'], 'fill', colors)

ag.write_SVG(x, w, h, 'svg/tiling2.svg')
ag.to_PNG('svg/tiling2.svg', 'png/tiling2.png')


######################################################################
# Polygon edges
######################################################################

outline = ag.circle(c=(200, 200), r=150)
colors = ag.Color(hue=ag.Uniform(min=0.6, max=0.8), sat=0.7,
                  li=ag.Uniform(min=0.5, max=0.7))
x = ag.tile_region(outline, shape='polygon', edges=True, tile_size=1000)
ag.set_style(x['members'], 'stroke', colors)
ag.set_style(x['members'], 'stroke-width', 2)

ag.write_SVG(x, w, h, 'svg/tiling3.svg')
ag.to_PNG('svg/tiling3.svg', 'png/tiling3.png')


######################################################################
# Triangle edges
######################################################################

outline = ag.circle(c=(200, 200), r=150)
color = ag.Color(hue=ag.Uniform(min=0.6, max=0.8), sat=0.7,
                 li=ag.Uniform(min=0.5, max=0.7))
x = ag.tile_region(outline, shape='triangle', edges=True, tile_size=1000)
ag.set_style(x['members'], 'stroke', color)
ag.set_style(x['members'], 'stroke-width', 2)

ag.write_SVG(x, w, h, 'svg/tiling4.svg')
ag.to_PNG('svg/tiling4.svg', 'png/tiling4.png')


######################################################################
# Nested triangles
######################################################################

outline = ag.circle(c=(200, 200), r=150)
color = ag.Color(hue=ag.Uniform(min=0, max=0.15), sat=0.8, li=0.5)
x = ag.fill_nested_triangles(outline, min_level=2, max_level=5, color=color)

ag.write_SVG(x, w, h, 'svg/tiling5.svg')
ag.to_PNG('svg/tiling5.svg', 'png/tiling5.png')
