import subprocess
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
from algoraphics.images import open_image, resize_image, image_regions
from algoraphics.images import region_color
from algoraphics.main import set_style
from algoraphics.color import rand_col_from_ranges
from algoraphics.svg import write_SVG

os.chdir(script_dir)

image = open_image("test_images.jpg")
resize_image(image, 800, None)
w, h = image.size

######################################################################
# Image segments colored from image
######################################################################

outlines = image_regions(image, smoothness=3)
for outline in outlines:
    color = region_color(outline, image)
    set_style(outline, 'fill', color)

write_SVG(outlines, w, h, 'svg/images1.svg')
subprocess.run(['convert', 'svg/images1.svg', 'png/images1.png'])
