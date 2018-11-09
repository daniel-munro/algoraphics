import subprocess
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
import algoraphics as ag

os.chdir(script_dir)

w = 400
h = 400

outline = ag.circle(c=(200, 200), r=150)

colors1 = ag.Color(hue=ag.Param(min=0, max=0.15), sat=0.8, li=0.5)
colors2 = ag.Color(hue=ag.Param(min=0.6, max=0.8), sat=0.7,
                   li=ag.Param(min=0.5, max=0.7))

######################################################################
# Polygon tiles
######################################################################

x = ag.tile_region(outline, ag.voronoi_regions, tile_size=500)
ag.set_style(x['members'], 'fill', colors1)
ag.write_SVG(x, w, h, 'svg/tiling1.svg')
subprocess.run(['convert', 'svg/tiling1.svg', 'png/tiling1.png'])


######################################################################
# Triangle tiles
######################################################################

x = ag.tile_region(outline, ag.delaunay_regions, tile_size=500)
ag.set_style(x['members'], 'fill', colors1)
ag.write_SVG(x, w, h, 'svg/tiling2.svg')
subprocess.run(['convert', 'svg/tiling2.svg', 'png/tiling2.png'])


######################################################################
# Polygon edges
######################################################################

x = ag.tile_region(outline, ag.voronoi_edges, tile_size=1000)
ag.set_style(x['members'], 'stroke', colors2)
ag.set_style(x['members'], 'stroke_width', 2)
ag.write_SVG(x, w, h, 'svg/tiling3.svg')
subprocess.run(['convert', 'svg/tiling3.svg', 'png/tiling3.png'])


######################################################################
# Triangle edges
######################################################################

x = ag.tile_region(outline, ag.delaunay_edges, tile_size=1000)
ag.set_style(x['members'], 'stroke', colors2)
ag.set_style(x['members'], 'stroke_width', 2)
ag.write_SVG(x, w, h, 'svg/tiling4.svg')
subprocess.run(['convert', 'svg/tiling4.svg', 'png/tiling4.png'])


######################################################################
# Nested triangles
######################################################################

x = ag.fill_nested_triangles(outline, min_level=2, max_level=5, color=colors1)
ag.write_SVG(x, w, h, 'svg/tiling5.svg')
subprocess.run(['convert', 'svg/tiling5.svg', 'png/tiling5.png'])


######################################################################
# Spot fill
######################################################################

x = ag.fill_ishihara_spots(outline)
ag.set_style(x, 'fill', colors2)
ag.write_SVG(x, w, h, 'svg/tiling6.svg')
subprocess.run(['convert', 'svg/tiling6.svg', 'png/tiling6.png'])
