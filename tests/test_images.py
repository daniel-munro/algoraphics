import subprocess
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
import algoraphics as ag

os.chdir(script_dir)

######################################################################
# Objects colored by sampling image
######################################################################

image = ag.open_image("test_images.jpg")
ag.resize_image(image, 800, None)
w, h = image.size
x = ag.tile_canvas(w, h, ag.voronoi_regions, tile_size=100)
ag.fill_shapes_from_image(x, image)

ag.write_SVG(x, w, h, 'svg/images1.svg')
subprocess.run(['convert', 'svg/images1.svg', 'png/images1.png'])


######################################################################
# Image segments colored from image
######################################################################

image = ag.open_image("test_images.jpg")
ag.resize_image(image, 800, None)
w, h = image.size
x = ag.image_regions(image, smoothness=3)
for outline in x:
    color = ag.region_color(outline, image)
    ag.set_style(outline, 'fill', color)
ag.add_paper_texture(x)

ag.write_SVG(x, w, h, 'svg/images2.svg')
subprocess.run(['convert', 'svg/images2.svg', 'png/images2.png'])


######################################################################
# TODO: test rand_col_nearby and contrasting_lightness
######################################################################
