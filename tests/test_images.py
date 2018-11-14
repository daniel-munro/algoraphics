import subprocess
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
import algoraphics as ag

os.chdir(script_dir)

image = ag.open_image("test_images.jpg")
ag.resize_image(image, 800, None)
w, h = image.size

######################################################################
# Image segments colored from image
######################################################################

outlines = ag.image_regions(image, smoothness=3)
for outline in outlines:
    color = ag.region_color(outline, image)
    ag.set_style(outline, 'fill', color)

ag.write_SVG(outlines, w, h, 'svg/images1.svg')
subprocess.run(['convert', 'svg/images1.svg', 'png/images1.png'])


######################################################################
# TODO: test rand_col_nearby and contrasting_lightness
######################################################################
