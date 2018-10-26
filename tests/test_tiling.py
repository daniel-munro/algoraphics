import subprocess
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
from algoraphics.tiling import tile_region, voronoi_regions, voronoi_edges
from algoraphics.tiling import delaunay_regions, delaunay_edges
from algoraphics.tiling import fill_nested_triangles, fill_ishihara_spots
from algoraphics.paths import circle
from algoraphics.main import set_style
from algoraphics.color import rand_col_from_ranges
from algoraphics.svg import write_SVG

os.chdir(script_dir)

w = 400
h = 400

outline = circle(c=(200, 200), r=150)

######################################################################
# Polygon tiles
######################################################################

x = tile_region(outline, voronoi_regions, tile_size=500)
set_style(x['members'], 'fill',
          lambda: rand_col_from_ranges(255, range(50, 200), 50))
write_SVG(x, w, h, 'svg/tiling1.svg')
subprocess.run(['convert', 'svg/tiling1.svg', 'png/tiling1.png'])


######################################################################
# Triangle tiles
######################################################################

x = tile_region(outline, delaunay_regions, tile_size=500)
set_style(x['members'], 'fill',
          lambda: rand_col_from_ranges(255, range(50, 200), 50))
write_SVG(x, w, h, 'svg/tiling2.svg')
subprocess.run(['convert', 'svg/tiling2.svg', 'png/tiling2.png'])


######################################################################
# Polygon edges
######################################################################

x = tile_region(outline, voronoi_edges, tile_size=1000)
set_style(x['members'], 'stroke',
          lambda: rand_col_from_ranges(range(50, 200), range(50, 200), 255))
set_style(x['members'], 'stroke_width', 2)
write_SVG(x, w, h, 'svg/tiling3.svg')
subprocess.run(['convert', 'svg/tiling3.svg', 'png/tiling3.png'])


######################################################################
# Triangle edges
######################################################################

x = tile_region(outline, delaunay_edges, tile_size=1000)
set_style(x['members'], 'stroke',
          lambda: rand_col_from_ranges(range(50, 200), range(50, 200), 255))
set_style(x['members'], 'stroke_width', 2)
write_SVG(x, w, h, 'svg/tiling4.svg')
subprocess.run(['convert', 'svg/tiling4.svg', 'png/tiling4.png'])


######################################################################
# Nested triangles
######################################################################

fill = lambda: rand_col_from_ranges(255, range(50, 200), 50)
x = fill_nested_triangles(outline, 2, 5, fill)
write_SVG(x, w, h, 'svg/tiling5.svg')
subprocess.run(['convert', 'svg/tiling5.svg', 'png/tiling5.png'])


######################################################################
# Spot fill
######################################################################

fill = lambda: rand_col_from_ranges(range(50, 200), range(50, 200), 255)
x = fill_ishihara_spots(outline)
set_style(x, 'fill', fill)
write_SVG(x, w, h, 'svg/tiling6.svg')
subprocess.run(['convert', 'svg/tiling6.svg', 'png/tiling6.png'])
